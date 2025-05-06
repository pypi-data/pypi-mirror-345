def is_pdf(f):
    return len(f) > 4 and b"%PDF" in f[:100]
