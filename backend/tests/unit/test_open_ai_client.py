import unittest
import os
from dotenv import load_dotenv
import json
from unittest.mock import patch
from src.services.llm_client.client import OpenAIClient
from src.services.llm_client.base import MessageInterface
from src.services.llm_client.enum import RelevanceLevel
from src.services.llm_client.exceptions import (
    LLMRequestFailedException,
    InvalidResponseFormatException,
    RelevanceLevelException
)

if not os.getenv("NEWS_OPEN_AI_KEY"):
    dotenv_path = os.path.join(os.path.dirname(__file__), "../../.env") 
    load_dotenv(dotenv_path)

# 除非確認要使用真實的API進行測試(當然會因此擁有額外的開銷)，否則將RUN_REAL_API_TESTS設置為False
RUN_REAL_API_TESTS = os.getenv("RUN_REAL_API_TESTS", "false").lower() == "true"


class TestOpenAIClient(unittest.TestCase):
    @classmethod
    def setUpClass(self):
        if RUN_REAL_API_TESTS:
            self.client = OpenAIClient(api_key=os.getenv("NEWS_OPEN_AI_KEY"))
        else:
            self.client = OpenAIClient(api_key="fake_api_key")

    @unittest.skipIf(not RUN_REAL_API_TESTS, "模擬 API 呼叫，跳過真實測試")
    def test_evaluate_relevance_real(self):
        result = self.client.evaluate_relevance("食品價格上漲")
        self.assertIn(result, RelevanceLevel)

    @unittest.skipIf(not RUN_REAL_API_TESTS, "模擬 API 呼叫，跳過真實測試")
    def test_generate_summary_real(self):
        result = self.client.generate_summary("近期，全球食品價格因氣候異常和供應鏈中斷而上漲，特別是穀物和蔬菜價格受到影響，消費者支出壓力增大。")
        self.assertIn("summary", result)
        self.assertIn("reason", result)

    @unittest.skipIf(not RUN_REAL_API_TESTS, "模擬 API 呼叫，跳過真實測試")
    def test_extract_search_keywords_real(self):
        result = self.client.extract_search_keywords("這篇新聞提到食品價格的波動以及市場的供應鏈問題")
        self.assertGreater(len(result.split()), 0)

    @patch('src.services.llm_client.client.OpenAIClient._generate_text')
    def test_evaluate_relevance(self, mock_generate_text):
        mock_generate_text.return_value = "high"

        result = self.client.evaluate_relevance("食品價格上漲")

        self.assertEqual(result, RelevanceLevel.HIGH)

        mock_generate_text.assert_called_once_with(
            messages=MessageInterface(
                system_content="你是一個關聯度評估機器人，請評估新聞標題是否與「民生用品的價格變化」相關，並給予'high'、'medium'、'low'評價。(僅需回答'high'、'medium'、'low'三個詞之一)",
                user_content="食品價格上漲"
            )
        )

    @patch('src.services.llm_client.client.OpenAIClient._generate_text')
    def test_generate_summary(self, mock_generate_text):
        mock_generate_text.return_value = '{"影響": "影響描述", "原因": "原因描述"}'

        result = self.client.generate_summary("一篇新聞內容")

        self.assertEqual(result, json.loads('{"summary": "影響描述", "reason": "原因描述"}'))

        mock_generate_text.assert_called_once_with(
            messages=MessageInterface(
                system_content='你是一個新聞摘要生成機器人，請統整新聞中提及的影響及主要原因 (影響、原因各50個字，請以json格式回答 {"影響": "...", "原因": "..."})',
                user_content="一篇新聞內容"
            )
        )

    @patch('src.services.llm_client.client.OpenAIClient._generate_text')
    def test_extract_search_keywords(self, mock_generate_text):
        mock_generate_text.return_value = '食品 價格'

        result = self.client.extract_search_keywords("一段希望看到的新聞文字")

        self.assertEqual(result, '食品 價格')

        mock_generate_text.assert_called_once_with(
            messages=MessageInterface(
                system_content="你是一個關鍵字提取機器人，用戶將會輸入一段文字，表示其希望看見的新聞內容，請提取出用戶希望看見的關鍵字，請截取最重要的關鍵字即可，避免出現「新聞」、「資訊」等混淆搜尋引擎的字詞。(僅須回答關鍵字，若有多個關鍵字，請以空格分隔)",
                user_content="一段希望看到的新聞文字"
            )
        )

    @patch('src.services.llm_client.client.OpenAIClient._generate_text')
    def test_generate_summary_invalid_json(self, mock_generate_text):
        mock_generate_text.return_value = '{"invalid_json": "missing_fields"}'

        with self.assertRaises(InvalidResponseFormatException):
            self.client.generate_summary("一篇新聞內容")

        mock_generate_text.assert_called_once()

    @patch('src.services.llm_client.client.OpenAIClient._generate_text')
    def test_evaluate_relevance_invalid_response(self, mock_generate_text):
        mock_generate_text.return_value = "invalid_level"

        with self.assertRaises(RelevanceLevelException):
            self.client.evaluate_relevance("食品價格上漲")

        mock_generate_text.assert_called_once()

    @patch('src.services.llm_client.client.OpenAIClient._generate_text')
    def test_extract_search_keywords_exception(self, mock_generate_text):
        mock_generate_text.side_effect = LLMRequestFailedException()

        with self.assertRaises(LLMRequestFailedException):
            self.client.extract_search_keywords("一段希望看到的新聞文字")

        mock_generate_text.assert_called_once()


if __name__ == '__main__':
    unittest.main()