import os
from typing import List, Dict, Optional
from openai import OpenAI


class DeepSeekClient:
    def __init__(self, api_base: str, api_key: str, default_model: str = "DeepSeek-V3") -> None:
        if not api_base or not api_key:
            raise ValueError("api_base 和 api_key 不能为空")
        self.client = OpenAI(base_url=api_base, api_key=api_key)
        self.default_model = default_model

    def chat(self, messages: List[Dict[str, str]], model: Optional[str] = None, temperature: float = 0.2, max_tokens: Optional[int] = None) -> str:
        model_name = model or self.default_model
        try:
            resp = self.client.chat.completions.create(
                model=model_name,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
            )
            return resp.choices[0].message.content or ""
        except Exception as e:
            # 记录到控制台，避免中断应用
            print(f"[DeepSeekClient.chat] 调用失败: {e}")
            return ""
