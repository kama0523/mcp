"""LLM呼び出しを担当するモジュール。

次の学習段階で、ユーザーの質問とMCPツール一覧をLLMへ渡し、
LLMが選んだツールをHostから実行する処理を追加します。
"""

from dotenv import load_dotenv
from openai import OpenAI


load_dotenv()

client = OpenAI()


def ask_llm(question: str) -> str:
    response = client.responses.create(
        model="gpt-5-nano",
        input=question,
    )

    return response.output_text


def main() -> None:
    question = input("LLMへの質問: ")
    answer = ask_llm(question)

    print("\nLLMの回答")
    print(answer)


if __name__ == "__main__":
    main()