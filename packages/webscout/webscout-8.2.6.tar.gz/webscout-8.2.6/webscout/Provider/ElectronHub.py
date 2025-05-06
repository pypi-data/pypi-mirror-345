from curl_cffi import CurlError
from curl_cffi.requests import Session
import json
import os
from typing import Any, Dict, Optional, Generator, Union, List

import requests

from webscout.AIutel import Optimizers
from webscout.AIutel import Conversation, sanitize_stream # Import sanitize_stream
from webscout.AIutel import AwesomePrompts, sanitize_stream
from webscout.AIbase import Provider, AsyncProvider
from webscout import exceptions
from webscout.litagent import LitAgent

class ElectronHub(Provider):
    """
    A class to interact with the ElectronHub API with LitAgent user-agent.
    """

    # Default models list (will be updated dynamically)
    AVAILABLE_MODELS = [
            # OpenAI GPT models
            "gpt-3.5-turbo",
            "gpt-3.5-turbo-16k",
            "gpt-3.5-turbo-1106",
            "gpt-3.5-turbo-0125",
            "gpt-4",
            "gpt-4-turbo",
            "gpt-4-turbo-preview",
            "gpt-4-0125-preview",
            "gpt-4-1106-preview",
            "gpt-4o",
            "gpt-4o-2024-05-13",
            "gpt-4o-2024-08-06",
            "gpt-4o-2024-11-20",
            "gpt-4o-search-preview",
            "gpt-4o-search-preview-2025-03-11",
            "gpt-4o-mini",
            "gpt-4o-mini-2024-07-18",
            "gpt-4o-mini-search-preview",
            "gpt-4o-mini-search-preview-2025-03-11",
            "chatgpt-4o-latest",
            "gpt-4.5-preview",
            "gpt-4.5-preview-2025-02-27",
            "o1-mini",
            "o1-preview",
            "o1",
            "o1-low",
            "o1-high",
            "o3-mini",
            "o3-mini-low",
            "o3-mini-high",
            "o3-mini-online",
            
            # Anthropic Claude models
            "claude-2",
            "claude-2.1",
            "claude-3-haiku-20240307",
            "claude-3-5-haiku-20241022",
            "claude-3-opus-20240229",
            "claude-3-sonnet-20240229",
            "claude-3-5-sonnet-20240620",
            "claude-3-5-sonnet-20241022",
            "claude-3-7-sonnet-20250219",
            "claude-3-7-sonnet-20250219-thinking",
            "claude-3-opus-20240229:safe",
            "claude-3-sonnet-20240229:safe",
            "claude-3-5-sonnet-20240620:safe",
            "claude-3-5-sonnet-20241022:safe",
            "claude-3-7-sonnet-20250219:safe",
            "claude-3-7-sonnet-20250219-thinking:safe",
            
            # Google Gemini models
            "gemini-1.0-pro",
            "gemini-1.0-pro-vision",
            "gemini-1.5-pro",
            "gemini-1.5-pro-latest",
            "gemini-1.5-flash-8b",
            "gemini-1.5-flash",
            "gemini-1.5-flash-latest",
            "gemini-1.5-flash-exp",
            "gemini-1.5-flash-online",
            "gemini-exp-1206",
            "learnlm-1.5-pro-experimental",
            "gemini-2.0-flash-001",
            "gemini-2.0-flash-exp",
            "gemini-2.0-flash-thinking-exp",
            "gemini-2.0-flash-thinking-exp-1219",
            "gemini-2.0-flash-thinking-exp-01-21",
            "gemini-2.0-flash-lite-preview-02-05",
            "gemini-2.0-flash-lite-001",
            "gemini-2.0-pro-exp-02-05",
            "gemini-2.5-pro-exp-03-25",
            
            # Google PaLM models
            "palm-2-chat-bison",
            "palm-2-codechat-bison",
            "palm-2-chat-bison-32k",
            "palm-2-codechat-bison-32k",
            
            # Meta Llama models
            "llama-2-13b-chat-awq",
            "llama-2-7b-chat-fp16",
            "llama-2-7b-chat-int8",
            "llama-2-70b-chat",
            "llama-3-8b-instruct",
            "llama-3-8b-instruct-awq",
            "llama-3-70b",
            "llama-3.1-8b-instruct",
            "llama-3.1-8b-instruct-awq",
            "llama-3.1-8b-instruct-fp8",
            "llama-3.1-70b",
            "llama-3.1-405b",
            "llama-3.2-11b-vision-instruct",
            "llama-3.2-1b-instruct",
            "llama-3.2-3b-instruct",
            "llama-3.2-90b",
            "llama-3.3-70b-instruct-fp8-fast",
            "llama-guard-3-8b",
            "llamaguard-7b-awq",
            "meta-llama-3-8b-instruct",
            "llama-3.1-nemotron-70b-instruct",
            "llama-3.1-tulu-3-70b",
            "llama-3.1-tulu-3-405b",
            "llama-3.1-sonar-small-128k-online",
            "llama-3.1-sonar-large-128k-online",
            "llama-3.1-sonar-huge-128k-online",
            "llama-3.1-sonar-small-128k-chat",
            "llama-3.1-sonar-large-128k-chat",
            "llama-3.1-swallow-70b-instruct-v0.3",
            "llama-3.1-8b-lexi-uncensored-v2",
            "llama-3.1-lumimaid-8b",
            "llama-3.1-lumimaid-70b",
            "llama3-openbiollm-70b",
            
            # Mistral models
            "mistral-7b-instruct-v0.1",
            "mistral-7b-instruct-v0.1-awq",
            "mistral-7b-instruct-v0.2",
            "mistral-tiny-latest",
            "mistral-tiny",
            "mistral-tiny-2312",
            "mistral-tiny-2407",
            "mistral-small-3.1-24b-instruct",
            "mistral-small-24b-instruct-2501",
            "mistral-small-latest",
            "mistral-small",
            "mistral-small-2312",
            "mistral-small-2402",
            "mistral-small-2409",
            "mistral-medium-latest",
            "mistral-medium",
            "mistral-medium-2312",
            "mistral-large-latest",
            "mistral-large-2411",
            "mistral-large-2407",
            "mistral-large-2402",
            "open-mistral-nemo",
            "open-mistral-nemo-2407",
            "open-mixtral-8x22b-2404",
            "open-mixtral-8x7b",
            
            # Codestral models
            "codestral-mamba",
            "codestral-latest",
            "codestral-2405",
            "codestral-2412",
            "codestral-2501",
            
            # Ministral models
            "ministral-3b",
            "ministral-3b-2410",
            "ministral-8b",
            "ministral-8b-2410",
            
            # Mistral Saba models
            "mistral-saba-latest",
            "mistral-saba-2502",
            
            # Mixtral models
            "mixtral-8x7b",
            "mixtral-8x22b",
            
            # DeepSeek models
            "deepseek-coder",
            "deepseek-coder-6.7b-base-awq",
            "deepseek-coder-6.7b-instruct-awq",
            "deepseek-llm-67b-chat",
            "deepseek-math-7b-instruct",
            "deepseek-r1",
            "deepseek-r1-distill-llama-70b",
            "deepseek-r1-distill-llama-8b",
            "deepseek-r1-distill-qwen-1.5b",
            "deepseek-r1-distill-qwen-14b",
            "deepseek-r1-distill-qwen-32b",
            "deepseek-r1-distill-qwen-7b",
            "deepseek-r1-nitro",
            "deepseek-r1-zero",
            "deepseek-v2.5",
            "deepseek-v3",
            "deepseek-v3-0324",
            "deepseek-vl2",
            
            # Qwen models
            "qwen-1.5-0.5b-chat",
            "qwen-1.5-1.8b-chat",
            "qwen-1.5-14b-chat-awq",
            "qwen-1.5-7b-chat-awq",
            "qwen-2-7b-instruct",
            "qwen-2-72b-instruct",
            "qwen-2-vl-7b-instruct",
            "qwen-2-vl-72b-instruct",
            "qwen-2.5-7b-instruct",
            "qwen-2.5-32b-instruct",
            "qwen-2.5-72b-instruct",
            "qwen-2.5-coder-32b-instruct",
            "qwq-32b-preview",
            "qwq-32b",
            "qwen-vl-plus",
            "qwen2.5-vl-3b-instruct",
            "qwen2.5-vl-7b-instruct",
            "qwen2.5-vl-72b-instruct",
            "qwen-turbo",
            "qwen-plus",
            "qwen-max",
            
            # F1 models
            "f1-mini-preview",
            "f1-preview",
            
            # Command models
            "command",
            "command-light",
            "command-nightly",
            "command-light-nightly",
            "command-r",
            "command-r-03-2024",
            "command-r-08-2024",
            "command-r-plus",
            "command-r-plus-04-2024",
            "command-r-plus-08-2024",
            "command-r7b-12-2024",
            "command-a-03-2025",
            
            # Dolphin models
            "dolphin-mixtral-8x7b",
            "dolphin-mixtral-8x22b",
            "dolphin3.0-mistral-24b",
            "dolphin3.0-r1-mistral-24b",
            
            # Cohere models
            "c4ai-aya-expanse-8b",
            "c4ai-aya-expanse-32b",
            
            # Reka models
            "reka-flash",
            "reka-core",
            "reka-flash-3",
            
            # OpenChat models
            "openchat-3.5-0106",
            "openchat-3.5-7b",
            "openchat-3.6-8b",
            
            # Yi models
            "yi-34b-chat-200k",
            "yi-large",
            "yi-large-rag",
            "yi-large-turbo",
            "yi-medium",
            "yi-vl-plus",
            
            # Phi models
            "phi-2",
            "phi-3-mini-128k-instruct",
            "phi-3-medium-128k-instruct",
            "phi-3.5-mini-128k-instruct",
            "phi-4",
            "phi-4-multimodal-instruct",
            
            # Claude models by AION-LABS
            "aion-1.0",
            "aion-1.0-mini",
            "aion-rp-llama-3.1-8b",
            
            # Other AI models
            "nemotron-4-340b",
            "pixtral-large-2411",
            "pixtral-12b",
            "dbrx-instruct",
            "grok-2",
            "grok-2-mini",
            "grok-beta",
            "grok-vision-beta",
            "grok-2-1212",
            "grok-2-vision-1212",
            "grok-3-early",
            "grok-3-preview-02-24",
            "r1-1776",
            "sonar-deep-research",
            "sonar-reasoning-pro",
            "sonar-reasoning",
            "sonar-pro",
            "sonar",
            "wizardlm-2-7b",
            "wizardlm-2-8x22b",
            "minimax-01",
            "jamba-1.5-large",
            "jamba-1.5-mini",
            "jamba-1.6-large",
            "jamba-1.6-mini",
            "jamba-instruct",
            
            # Chinese language models
            "doubao-lite-4k",
            "doubao-lite-32k",
            "doubao-pro-4k",
            "doubao-pro-32k",
            "ui-tars-72b-dpo",
            "ernie-lite-8k",
            "ernie-tiny-8k",
            "ernie-speed-8k",
            "ernie-speed-128k",
            "hunyuan-lite",
            "hunyuan-standard-2025-02-10",
            "hunyuan-large-2025-02-10",
            "glm-3-130b",
            "glm-4-flash",
            "glm-4-long",
            "glm-4-airx",
            "glm-4-air",
            "glm-4-plus",
            "glm-4-alltools",
            "spark-desk-v1.5",
            
            # Other language models
            "discolm-german-7b-v1-awq",
            "falcon-7b-instruct",
            "neural-chat-7b-v3-1-awq",
            "openhermes-2.5-mistral-7b",
            "openhermes-2.5-mistral-7b-awq",
            "sqlcoder-7b-2",
            "starling-lm-7b-beta",
            "tinyllama-1.1b-chat-v1.0",
            "una-cybertron-7b-v2-bf16",
            "zephyr-7b-beta",
            "zephyr-7b-beta-awq",
            
            # Inference-optimized models
            "mistral-nemo-inferor-12b",
            "rocinante-12b-v1",
            "rocinante-12b-v1.1",
            "unslopnemo-12b",
            
            # Additional specialty models
            "granite-3.1-2b-instruct",
            "granite-3.1-8b-instruct",
            "solar-0-70b-16bit",
            "olympiccoder-7b",
            "olympiccoder-32b",
            "anubis-pro-105b-v1",
            "fallen-llama-3.3-r1-70b-v1",
            "skyfall-36b-v2",
            "wayfarer-large-70b-llama-3.3",
            "qwq-32b-snowdrop-v0",
            "qwq-32b-abliterated",
            "sky-t1-32b-preview",
            "tiny-r1-32b-preview",
            "lfm-3b",
            "lfm-7b",
            "lfm-40b",
            "eva-llama-3.33-70b-v0.0",
            "eva-llama-3.33-70b-v0.1",
            "eva-qwen2.5-72b",
            "eva-qwen2.5-32b-v0.2",
            "sorcererlm-8x22b",
            "mythalion-13b",
            "toppy-m-7b",
            "l3-lunaris-8b",
            "l3.1-70b-hanami-x1",
            "lumimaid-magnum-v4-12b",
            "magnum-v4-72b",
            "magnum-v4-12b",
            "magnum-v3-34b",
            "magnum-v2.5-12b-kto",
            "magnum-v2-72b",
            "magnum-v2-32b",
            "magnum-v2-12b",
            "magnum-72b",
            "mini-magnum-12b-v1.1",
            "remm-slerp-l2-13b",
            "patricide-12b-unslop-mell",
            "midnight-rose-70b",
            "airoboros-l2-13b-gpt4-m2.0",
            "airoboros-l2-70b",
            "xwin-lm-70b",
            "noromaid-20b",
            "violet-twilight-v0.2",
            "saiga-nemo-12b",
            "l3-8b-stheno-v3.2",
            "l3.3-electra-r1-70b",
            "l3.3-cu-mai-r1-70b",
            "l3.3-mokume-gane-r1-70b-v1.1",
            "l3.3-70b-euryale-v2.3",
            "l3.3-ms-evayale-70b",
            "70b-l3.3-cirrus-x1",
            "l31-70b-euryale-v2.2",
            "l3-70b-euryale-v2.1",
            "fimbulvetr-11b-v2",
            "goliath-120b",
            "hermes-2-pro-mistral-7b",
            "mytho-max-l2-13b",
            "deephermes-3-llama-3-8b-preview",
            "nous-hermes-llama2-13b",
            "hermes-3-llama-3.1-405b",
            "nous-hermes-2-mixtral-8x7b-dpo",
            "nova-lite-v1",
            "nova-micro-v1",
            "nova-pro-v1",
            "inflection-3-pi",
            "inflection-3-productivity",
            
            # Image generation models
            "weaver",
            "sdxl",
            "sdxl-turbo",
            "sdxl-lightning",
            "stable-diffusion-3",
            "stable-diffusion-3-2b",
            "stable-diffusion-3.5-large",
            "stable-diffusion-3.5-turbo",
            "playground-v3",
            "playground-v2.5",
            "animaginexl-3.1",
            "realvisxl-4.0",
            "imagen",
            "imagen-3-fast",
            "imagen-3",
            "luma-photon",
            "luma-photon-flash",
            "recraft-20b",
            "recraft-v3",
            "grok-2-aurora",
            "flux-schnell",
            "flux-dev",
            "flux-pro",
            "flux-1.1-pro",
            "flux-1.1-pro-ultra",
            "flux-1.1-pro-ultra-raw",
            "flux-realism",
            "flux-half-illustration",
            "ideogram-v2-turbo",
            "ideogram-v2",
            "amazon-titan",
            "amazon-titan-v2",
            "nova-canvas",
            "omni-gen",
            "aura-flow",
            "cogview-3-flash",
            "sana",
            "kandinsky-3",
            "dall-e-3",
            "midjourney-v6.1",
            "midjourney-v6",
            "midjourney-v5.2",
            "midjourney-v5.1",
            "midjourney-v5",
            "midjourney-v7",
            "niji-v6",
            "niji-v5",
            
            # Video generation models
            "t2v-turbo",
            "cogvideox-5b",
            "ltx-video",
            "mochi-1",
            "dream-machine",
            "hailuo-ai",
            "haiper-video-2.5",
            "haiper-video-2",
            "hunyuan-video",
            "kling-video/v1/standard/text-to-video",
            "kling-video/v1/pro/text-to-video",
            "kling-video/v1.6/standard/text-to-video",
            "kling-video/v1.5/pro/text-to-video",
            "kokoro-82m",
            
            # Audio models
            "elevenlabs",
            "myshell-tts",
            "deepinfra-tts",
            "whisper-large-v3",
            "distil-large-v3",
            
            # Embedding and moderation models
            "text-embedding-3-large",
            "text-embedding-3-small",
            "omni-moderation-latest",
            "omni-moderation-2024-09-26",
            "text-moderation-latest",
            "text-moderation-stable",
            "text-moderation-007"
        ]
        
    @classmethod
    def get_models(cls, api_key: str = None):
        """Fetch available models from ElectronHub API.
        
        Args:
            api_key (str, optional): ElectronHub API key. If not provided, returns default models.
            
        Returns:
            list: List of available model IDs
        """
        if not api_key:
            return cls.AVAILABLE_MODELS
            
        try:
            headers = {
                'Content-Type': 'application/json',
                'Accept': '*/*',
                'User-Agent': LitAgent().random(),
                'Authorization': f'Bearer {api_key}'
            }
            
            response = requests.get(
                "https://api.electronhub.top/v1/models",
                headers=headers,
                timeout=10
            )
            
            if response.status_code != 200:
                return cls.AVAILABLE_MODELS
                
            data = response.json()
            if "data" in data and isinstance(data["data"], list):
                return [model["id"] for model in data["data"]]
            return cls.AVAILABLE_MODELS
            
        except Exception:
            # Fallback to default models list if fetching fails
            return cls.AVAILABLE_MODELS
    
    @classmethod
    def update_available_models(cls, api_key=None):
        """Update the available models list from ElectronHub API"""
        try:
            models = cls.get_models(api_key)
            if models and len(models) > 0:
                cls.AVAILABLE_MODELS = models
        except Exception:
            # Fallback to default models list if fetching fails
            pass

    @staticmethod
    def _electronhub_extractor(chunk: Union[str, Dict[str, Any]]) -> Optional[str]:
        """Extracts content from ElectronHub stream JSON objects."""
        if isinstance(chunk, dict):
            return chunk.get("choices", [{}])[0].get("delta", {}).get("content")
        return None

    def __init__(
        self,
        is_conversation: bool = True,
        max_tokens: int = 16000,
        timeout: int = 30,
        intro: str = None,
        filepath: str = None,
        update_file: bool = True,
        proxies: dict = {},
        history_offset: int = 10250,
        act: str = None,
        model: str = "claude-3-7-sonnet-20250219",
        system_prompt: str = "You're helpful assistant that can help me with my questions.",
        api_key: str = None
    ):
        """Initializes the ElectronHub API client."""
        # Update available models from API
        self.update_available_models(api_key)
        
        # Validate model after updating available models
        if model not in self.AVAILABLE_MODELS:
            raise ValueError(f"Invalid model: {model}. Choose from: {self.AVAILABLE_MODELS}")
            
        self.url = "https://api.electronhub.top/v1/chat/completions"
        # Use LitAgent for user-agent
        self.headers = {
            'User-Agent': LitAgent().random(),
            'Content-Type': 'application/json',
            'Accept': '*/*',
            'Accept-Language': 'en-US,en;q=0.9',
            'DNT': '1',
            'Origin': 'https://playground.electronhub.top',
            'Referer': 'https://playground.electronhub.top/',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-site',
            'Priority': 'u=1, i'
        }
        
        # Add API key if provided
        if api_key:
            self.headers['Authorization'] = f'Bearer {api_key}'
        self.system_prompt = system_prompt
        self.session = Session() # Use curl_cffi Session
        self.session.headers.update(self.headers)
        self.session.proxies = proxies # Assign proxies directly

        self.is_conversation = is_conversation
        self.max_tokens = max_tokens
        self.timeout = timeout
        self.last_response = {}
        self.model = model

        self.__available_optimizers = (
            method
            for method in dir(Optimizers)
            if callable(getattr(Optimizers, method)) and not method.startswith("__")
        )
        Conversation.intro = (
            AwesomePrompts().get_act(
                act, raise_not_found=True, default=None, case_insensitive=True
            )
            if act
            else intro or Conversation.intro
        )

        self.conversation = Conversation(
            is_conversation, self.max_tokens, filepath, update_file
        )
        self.conversation.history_offset = history_offset

    def ask(
        self,
        prompt: str,
        stream: bool = True,
        raw: bool = False,
        optimizer: str = None,
        conversationally: bool = False,
        temperature: float = 0.5,
        top_p: float = 1.0,
        top_k: int = 5,
    ) -> Union[Dict[str, Any], Generator]:
        conversation_prompt = self.conversation.gen_complete_prompt(prompt)
        if optimizer:
            if optimizer in self.__available_optimizers:
                conversation_prompt = getattr(Optimizers, optimizer)(
                    conversation_prompt if conversationally else prompt
                )
            else:
                raise Exception(f"Optimizer is not one of {self.__available_optimizers}")

        # Construct messages for the conversation
        messages = [
            {"role": "system", "content": self.system_prompt},
            {"role": "user", "content": [{"type": "text", "text": conversation_prompt}]}
        ]

        # Payload construction based on ElectronHub API requirements
        payload = {
            "model": self.model,
            "messages": messages,
            "stream": stream,
            "stream_options": {"include_usage": True},
            "max_tokens": self.max_tokens,
            "temperature": temperature,
            "top_p": top_p,
            "top_k": top_k,
            "web_search": False,
            "customId": None
        }

        def for_stream():
            try:
                response = self.session.post(
                    self.url, headers=self.headers, data=json.dumps(payload), stream=True, timeout=self.timeout,
                    impersonate="chrome120" # Add impersonate
                )
                response.raise_for_status()

                streaming_text = ""
                # Use sanitize_stream
                processed_stream = sanitize_stream(
                    data=response.iter_content(chunk_size=None), # Pass byte iterator
                    intro_value="data:",
                    to_json=True,     # Stream sends JSON
                    skip_markers=["[DONE]"],
                    content_extractor=self._electronhub_extractor, # Use the specific extractor
                    yield_raw_on_error=False # Skip non-JSON lines or lines where extractor fails
                )

                for content_chunk in processed_stream:
                    # content_chunk is the string extracted by _electronhub_extractor
                    if content_chunk and isinstance(content_chunk, str):
                        streaming_text += content_chunk
                        resp = dict(text=content_chunk)
                        yield resp if not raw else content_chunk

            except CurlError as e:
                raise exceptions.FailedToGenerateResponseError(f"Request failed (CurlError): {str(e)}") from e
            except Exception as e:
                raise exceptions.FailedToGenerateResponseError(f"Request failed: {str(e)}")
            finally:
                # Update history after stream finishes or fails
                if streaming_text:
                    self.conversation.update_chat_history(prompt, streaming_text)

        def for_non_stream():
            collected_response = ""
            try:
                for chunk in for_stream():
                    if isinstance(chunk, dict) and "text" in chunk:
                        content = chunk["text"]
                        if content is not None:
                            collected_response += content
            except Exception as e:
                raise exceptions.FailedToGenerateResponseError(f"Error during non-stream processing: {str(e)}")
            
            # Update history and last_response after aggregation
            self.last_response = {"text": collected_response}
            self.conversation.update_chat_history(prompt, collected_response)
            return self.last_response

        return for_stream() if stream else for_non_stream()

    def chat(
        self,
        prompt: str,
        stream: bool = True,
        optimizer: str = None,
        conversationally: bool = False,
        temperature: float = 0.5,
        top_p: float = 1.0,
        top_k: int = 5,
    ) -> str:
        def for_stream():
            for response in self.ask(
                prompt, 
                True, 
                optimizer=optimizer, 
                conversationally=conversationally,
                temperature=temperature,
                top_p=top_p,
                top_k=top_k
            ):
                yield self.get_message(response)
        def for_non_stream():
            return self.get_message(
                self.ask(
                    prompt, 
                    False, 
                    optimizer=optimizer, 
                    conversationally=conversationally,
                    temperature=temperature,
                    top_p=top_p,
                    top_k=top_k
                )
            )
        return for_stream() if stream else for_non_stream()

    def get_message(self, response: dict) -> str:
        assert isinstance(response, dict), "Response should be of dict data-type only"
        return response["text"]

if __name__ == "__main__":
    from rich import print
    # You need to provide your own API key
    api_key = ""  # U can get free API key from https://playground.electronhub.top/console
    ai = ElectronHub(timeout=5000, api_key=api_key)
    response = ai.chat("hi there, how are you today?", stream=True)
    for chunk in response:
        print(chunk, end="", flush=True)