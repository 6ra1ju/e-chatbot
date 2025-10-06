from process_data import chat, ingest
if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "ingest":
        ingest("data")
    else:
        chat()