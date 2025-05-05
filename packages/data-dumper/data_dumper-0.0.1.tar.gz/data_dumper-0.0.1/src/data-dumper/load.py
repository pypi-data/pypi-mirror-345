def load(data,file):
    try:
        file.load(data)
    except Exception:
        raise
    else:
        return None
    finally:
        file.close()
