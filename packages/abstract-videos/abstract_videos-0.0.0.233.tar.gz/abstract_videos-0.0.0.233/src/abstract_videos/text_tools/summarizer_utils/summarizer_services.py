from ..routes import *
def chunk_summaries(chunks, max_length=None, min_length=None, truncation=True):  # Enabled truncation by default
    max_length = max_length or 100  # Reduced max_length
    min_length = min_length or 50  # Increased min_length for balance
    summaries = []
    for idx, chunk in enumerate(chunks):
        out = summarizer(
            chunk,
            max_length=max_length,
            min_length=min_length,
            truncation=truncation
        )
        summaries.append(out[0]["summary_text"])
    return summaries

def split_to_chunk(full_text, max_words=None):
    max_words = max_words or 200  # Reduced max_words
    sentences = full_text.split(". ")
    chunks, buf = [], ""
    for sent in sentences:
        if len((buf + sent).split()) <= max_words:
            buf += sent + ". "
        else:
            chunks.append(buf.strip())
            buf = sent + ". "
    if buf:
        chunks.append(buf.strip())
    return chunks
def get_summary(
    full_text,
    keywords=None,
    max_words=None,
    max_length=None,
    min_length=None,
    truncation=True
):
    summary = None
    if full_text and summarizer:
        chunks = split_to_chunk(full_text, max_words=max_words)
        summaries = chunk_summaries(
            chunks,
            max_length=max_length,
            min_length=min_length,
            truncation=truncation
        )
        # Stitch and enforce total word limit
        summary = " ".join(summaries).strip()
        # Post-process to limit total summary to 150 words
        words = summary.split()
        if len(words) > 150:
            summary = " ".join(eatAllQuotes(words[:150])) + "..."
    return summary
