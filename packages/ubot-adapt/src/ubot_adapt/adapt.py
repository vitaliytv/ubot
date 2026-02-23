"""Адаптація тексту за допомогою Llama-3.1-8B-Instruct."""

import logging
import os

from transformers import AutoModelForCausalLM, AutoTokenizer

logger = logging.getLogger(__name__)

MODEL_ID = "meta-llama/Llama-3.1-8B-Instruct"
MAX_INPUT_TOKENS = 3000
MAX_NEW_TOKENS = 2048

_ADAPTER = None


def _get_adapter():
    global _ADAPTER
    if _ADAPTER is None:
        token = os.getenv("HF_TOKEN") or os.getenv("HUGGING_FACE_HUB_TOKEN")
        logger.info("Завантаження моделі %s…", MODEL_ID)
        tokenizer = AutoTokenizer.from_pretrained(MODEL_ID, token=token)
        model = AutoModelForCausalLM.from_pretrained(
            MODEL_ID,
            token=token,
            torch_dtype="auto",
            device_map="auto",
        )
        _ADAPTER = (tokenizer, model)
    return _ADAPTER


ADAPTATION_SYSTEM = """You are a text adapter. Given raw text exported from a PDF, produce an adapted version that:
- Removes dry technical fragments
- Splits content into logical blocks
- Rewrites complex sentences more simply
- Adds clarifications and short explanatory phrases where helpful
- Turns bullet lists into flowing text description where appropriate
- Adds clear headings, pauses, and short intros between sections
- Removes duplicates and irrelevant fragments

Output only the adapted text, in the same language as the input. Preserve meaning; do not add external information."""


def adapt_text(text: str) -> str:
    """
    Адаптує текст за чеклістом (логічні блоки, спрощення, заголовки тощо).
    Використовує Llama-3.1-8B-Instruct.
    """
    if not text or not text.strip():
        return ""
    tokenizer, model = _get_adapter()
    content = text[:20000]
    messages = [
        {"role": "system", "content": ADAPTATION_SYSTEM},
        {"role": "user", "content": f"Adapt this text:\n\n{content}"},
    ]
    prompt = tokenizer.apply_chat_template(
        messages,
        tokenize=False,
        add_generation_prompt=True,
    )
    inputs = tokenizer(
        prompt,
        return_tensors="pt",
        truncation=True,
        max_length=MAX_INPUT_TOKENS,
    ).to(model.device)
    out = model.generate(
        **inputs,
        max_new_tokens=MAX_NEW_TOKENS,
        do_sample=True,
        temperature=0.6,
        top_p=0.9,
        pad_token_id=tokenizer.eos_token_id,
    )
    reply = tokenizer.decode(out[0][inputs["input_ids"].shape[1] :], skip_special_tokens=True)
    reply = reply.strip()
    input_tokens = inputs["input_ids"].shape[1]
    output_tokens = out.shape[1] - input_tokens
    logger.info(
        "Адаптація: вхід %d токенів, згенеровано %d токенів, результат %d символів",
        input_tokens,
        output_tokens,
        len(reply),
    )
    if not reply:
        raw = tokenizer.decode(out[0][inputs["input_ids"].shape[1] :], skip_special_tokens=False)
        logger.warning("Модель повернула порожній текст після strip. Сирий вивід (первые 200 сим): %r", raw[:200])
    return reply
