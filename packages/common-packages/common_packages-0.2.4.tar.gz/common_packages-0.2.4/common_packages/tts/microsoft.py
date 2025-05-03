import requests


class TTSMicrosoft:
    """[参考](https://learn.microsoft.com/en-us/azure/ai-services/speech-service/index-text-to-speech)
    [获取指定区域的语音列表,比如日本西](https://japanwest.tts.speech.microsoft.com/cognitiveservices/voices/list)
    """

    def __init__(self, key: str, location_region: str) -> None:
        # 查看自己的服务
        self.location_region = location_region
        self.key = key
        # app name
        self.user_agent = "language_backend"

        # 获取token的url, 该url可能不存在
        self.access_token_url = f"https://{self.location_region}.api.cognitive.microsoft.com/sts/v1.0/issueToken"
        # 文本转语音的url, 该url可能不存在
        self.txt_to_speech_url = f"https://{self.location_region}.tts.speech.microsoft.com/cognitiveservices/v1"

        # 输出音频风格: 当前是美国英语，男性，Andrew Multilingual
        self.language_code = "en-US"
        self.gender = "Male"
        self.name = "en-US-AndrewMultilingualNeural"
        # 输出格式,当前是: 非流式，24赫兹
        self.output_format = "riff-24khz-16bit-mono-pcm"

    def fetch_access_token(self):
        """获取转换文本时,携带的access token"""
        request = requests.post(
            self.access_token_url,
            headers={
                "Ocp-Apim-Subscription-Key": self.key,
            },
        )
        return request.text

    def generate_xml_data(self, text: str):
        """将要转换的文本封装为xml格式"""
        data = f"""
        <speak version='1.0' xml:lang='{self.language_code}'>
            <voice xml:lang='{self.language_code}' xml:gender='{self.gender}'
            name='{self.name}'>
                {text}
            </voice>
        </speak>
        """
        return data

    def convert_text_to_speech(self, text: str) -> bytes:
        """将文本转换为语音"""
        r = requests.post(
            self.txt_to_speech_url,
            headers={
                "Content-Type": "application/ssml+xml",
                "X-Microsoft-OutputFormat": self.output_format,
                "User-Agent": self.user_agent,
                "Authorization": f"Bearer {self.fetch_access_token()}",
            },
            data=self.generate_xml_data(text),
        )
        return r.content
