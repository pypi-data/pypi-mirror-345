"""
方法论管理模块
该模块提供了加载和搜索方法论的实用工具。
包含以下功能：
- 加载和处理方法论数据
- 生成方法论临时文件
- 上传方法论文件到大模型
"""
import os
import json
import tempfile
from typing import Dict, Optional

from jarvis.jarvis_utils.config import INPUT_WINDOW_REVERSE_SIZE, get_max_input_token_count, get_data_dir
from jarvis.jarvis_utils.embedding import get_context_token_count
from jarvis.jarvis_utils.output import PrettyOutput, OutputType
from jarvis.jarvis_platform.registry import PlatformRegistry

def _get_methodology_directory() -> str:
    """
    获取方法论目录路径，如果不存在则创建

    返回：
        str: 方法论目录的路径
    """
    methodology_dir = os.path.join(get_data_dir(), "methodologies")
    if not os.path.exists(methodology_dir):
        try:
            os.makedirs(methodology_dir, exist_ok=True)
        except Exception as e:
            PrettyOutput.print(f"创建方法论目录失败: {str(e)}", OutputType.ERROR)
    return methodology_dir

def _load_all_methodologies() -> Dict[str, str]:
    """
    加载所有方法论文件

    返回：
        Dict[str, str]: 方法论字典，键为问题类型，值为方法论内容
    """
    methodology_dir = _get_methodology_directory()
    all_methodologies = {}

    if not os.path.exists(methodology_dir):
        return all_methodologies

    import glob
    for filepath in glob.glob(os.path.join(methodology_dir, "*.json")):
        try:
            with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
                methodology = json.load(f)
                problem_type = methodology.get("problem_type", "")
                content = methodology.get("content", "")
                if problem_type and content:
                    all_methodologies[problem_type] = content
        except Exception as e:
            filename = os.path.basename(filepath)
            PrettyOutput.print(f"加载方法论文件 {filename} 失败: {str(e)}", OutputType.WARNING)

    return all_methodologies

def _create_methodology_temp_file(methodologies: Dict[str, str]) -> Optional[str]:
    """
    创建包含所有方法论的临时文件

    参数：
        methodologies: 方法论字典，键为问题类型，值为方法论内容

    返回：
        Optional[str]: 临时文件路径，如果创建失败则返回None
    """
    if not methodologies:
        return None
    
    try:
        # 创建临时文件
        fd, temp_path = tempfile.mkstemp(suffix='.md', prefix='methodologies_')
        os.close(fd)
        
        # 写入方法论内容
        with open(temp_path, 'w', encoding='utf-8') as f:
            f.write("# 方法论集合\n\n")
            for problem_type, content in methodologies.items():
                f.write(f"## {problem_type}\n\n")
                f.write(f"{content}\n\n")
                f.write("---\n\n")
            f.flush()
        
        return temp_path
    except Exception as e:
        PrettyOutput.print(f"创建方法论临时文件失败: {str(e)}", OutputType.ERROR)
        return None

def load_methodology(user_input: str) -> str:
    """
    加载方法论并上传到大模型。

    参数：
        user_input: 用户输入文本，用于提示大模型

    返回：
        str: 相关的方法论提示，如果未找到方法论则返回空字符串
    """
    from yaspin import yaspin

    # 获取方法论目录
    methodology_dir = _get_methodology_directory()
    if not os.path.exists(methodology_dir):
        return ""

    try:
        # 加载所有方法论
        with yaspin(text="加载方法论文件...", color="yellow") as spinner:
            methodologies = _load_all_methodologies()
            if not methodologies:
                spinner.text = "没有找到方法论文件"
                spinner.fail("❌")
                return ""
            spinner.text = f"加载方法论文件完成 (共 {len(methodologies)} 个)"
            spinner.ok("✅")

        # 获取当前平台
        platform = PlatformRegistry().get_normal_platform()
        
        # 检查是否需要特殊处理大文件
        if get_context_token_count(user_input) > get_max_input_token_count() - INPUT_WINDOW_REVERSE_SIZE:
            # 创建临时文件
            with yaspin(text="创建方法论临时文件...", color="yellow") as spinner:
                temp_file_path = _create_methodology_temp_file(methodologies)
                if not temp_file_path:
                    spinner.text = "创建方法论临时文件失败"
                    spinner.fail("❌")
                    return ""
                spinner.text = f"创建方法论临时文件完成: {temp_file_path}"
                spinner.ok("✅")

            # 尝试上传文件
            upload_success = False
            try:
                if platform.upload_files([temp_file_path]):
                    upload_success = True
                    spinner.write("✅ 成功上传方法论文件")
                else:
                    spinner.write("⚠️ 上传方法论文件失败，将使用chat_with_files处理")
            except Exception as e:
                spinner.write(f"⚠️ 上传文件时出错: {str(e)}")
                upload_success = False

            # 构建提示信息
            prompt = f"""请根据以下方法论内容，总结出与以下用户需求相关的方法论: {user_input}

请按以下格式回复：
### 与该任务/需求相关的方法论
1. [方法论名字]
2. [方法论名字]
### 根据以上方法论，总结出方法论内容
[总结的方法论内容]

如果没有匹配的方法论，请输出：没有历史方法论可参考
除以上要求外，不要输出任何内容"""

            if upload_success:
                # 使用上传的文件
                return platform.chat_until_success(prompt)
            else:
                # 使用chat_with_files处理大文件
                from jarvis.jarvis_utils.utils import chat_with_files
                return chat_with_files([temp_file_path], platform, prompt, "")
        else:
            # 上下文足够，直接在prompt中包含方法论内容
            prompt = f"""以下是所有可用的方法论内容：

"""
            for problem_type, content in methodologies.items():
                prompt += f"## {problem_type}\n\n{content}\n\n---\n\n"
            
            prompt += f"""
请根据以上方法论内容，总结出与以下用户需求相关的方法论: {user_input}

请按以下格式回复：
### 与该任务/需求相关的方法论
1. [方法论名字]
2. [方法论名字]
### 根据以上方法论，总结出方法论内容
[总结的方法论内容]

如果没有匹配的方法论，请输出：没有历史方法论可参考
除以上要求外，不要输出任何内容"""
            return platform.chat_until_success(prompt)
    
    except Exception as e:
        PrettyOutput.print(f"加载方法论失败: {str(e)}", OutputType.ERROR)
        # 清理临时文件
        if 'temp_file_path' in locals() and temp_file_path and os.path.exists(temp_file_path):
            try:
                os.remove(temp_file_path)
            except:
                pass
        return ""
    finally:
        # 确保清理临时文件
        if 'temp_file_path' in locals() and temp_file_path and os.path.exists(temp_file_path):
            try:
                os.remove(temp_file_path)
            except:
                pass
