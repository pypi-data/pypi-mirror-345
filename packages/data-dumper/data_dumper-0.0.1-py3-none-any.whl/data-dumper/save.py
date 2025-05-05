def save(data,file):
    try:
        file.dump(data)
    except Exception:
        raise
    except:
        pass
    else:
        return None
    finally:
        file.flush()
