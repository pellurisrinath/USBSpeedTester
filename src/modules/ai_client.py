import urllib.request
import urllib.error
import json
import sys

class AIClient:
    def __init__(self, provider, api_key, model, endpoint):
        self.provider = provider.lower()
        self.api_key = api_key
        self.model = model
        self.endpoint = endpoint.rstrip('/')

    def _send_request(self, url, headers, data, method="POST"):
        """Utility to send HTTP request using Python's built-in urllib.request"""
        json_data = json.dumps(data).encode('utf-8')
        req = urllib.request.Request(url, data=json_data, headers=headers, method=method)
        try:
            with urllib.request.urlopen(req, timeout=300) as response:
                res_body = response.read().decode('utf-8')
                return json.loads(res_body)
        except urllib.error.HTTPError as e:
            # Try to read error body for detail
            try:
                err_body = e.read().decode('utf-8')
                err_json = json.loads(err_body)
                error_msg = err_json.get('error', {}).get('message', err_body)
            except:
                error_msg = e.reason
            raise Exception(f"HTTP Error {e.code}: {error_msg}")
        except urllib.error.URLError as e:
            raise Exception(f"Connection failed: {e.reason}")
        except Exception as e:
            raise Exception(f"Request failed: {str(e)}")

    def get_response(self, chat_history):
        """Sends chat history to LLM provider and returns reply text"""
        
        # 1. Ollama
        if self.provider == 'ollama':
            url = f"{self.endpoint}/api/chat"
            headers = {"Content-Type": "application/json"}
            data = {
                "model": self.model,
                "messages": chat_history,
                "stream": False
            }
            res = self._send_request(url, headers, data)
            return res.get("message", {}).get("content", "")

        # 2. Anthropic Claude
        elif self.provider == 'claude' or self.provider == 'anthropic':
            url = f"{self.endpoint}/v1/messages"
            headers = {
                "Content-Type": "application/json",
                "x-api-key": self.api_key,
                "anthropic-version": "2023-06-01"
            }
            # System prompt is passed separately in Claude API
            system_prompt = ""
            messages = []
            for msg in chat_history:
                if msg["role"] == "system":
                    system_prompt = msg["content"]
                else:
                    messages.append({
                        "role": msg["role"],
                        "content": msg["content"]
                    })
            data = {
                "model": self.model,
                "max_tokens": 2048,
                "messages": messages
            }
            if system_prompt:
                data["system"] = system_prompt
                
            res = self._send_request(url, headers, data)
            content = res.get("content", [])
            if content and isinstance(content, list):
                return content[0].get("text", "")
            return ""

        # 3. Google Gemini
        elif self.provider == 'gemini' or self.provider == 'google':
            # Gemini models generateContent API endpoint
            # Gemini expects url format: https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}
            url = f"{self.endpoint}/v1beta/models/{self.model}:generateContent?key={self.api_key}"
            headers = {"Content-Type": "application/json"}
            
            # Convert system and chat history to Gemini's content format
            gemini_contents = []
            system_instruction = None
            
            for msg in chat_history:
                if msg["role"] == "system":
                    system_instruction = {
                        "parts": [{"text": msg["content"]}]
                    }
                else:
                    role = "model" if msg["role"] == "assistant" else msg["role"]
                    gemini_contents.append({
                        "role": role,
                        "parts": [{"text": msg["content"]}]
                    })
            
            data = {
                "contents": gemini_contents
            }
            if system_instruction:
                data["systemInstruction"] = system_instruction
                
            res = self._send_request(url, headers, data)
            candidates = res.get("candidates", [])
            if candidates:
                parts = candidates[0].get("content", {}).get("parts", [])
                if parts:
                    return parts[0].get("text", "")
            return ""

        # 4. OpenAI & compatible (DeepSeek, Groq, OpenRouter, Mistral, LM Studio, etc.)
        else:
            url = f"{self.endpoint}/v1/chat/completions"
            headers = {"Content-Type": "application/json"}
            if self.api_key:
                headers["Authorization"] = f"Bearer {self.api_key}"
            
            data = {
                "model": self.model,
                "messages": chat_history
            }
            res = self._send_request(url, headers, data)
            choices = res.get("choices", [])
            if choices:
                return choices[0].get("message", {}).get("content", "")
            return ""
