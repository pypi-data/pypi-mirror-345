import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

from logthis import log_info, log_warn, log_error, enable_file_logging

def test_log_functions():
    
    enable_file_logging("logs/test_logthis.log")
    
    print("Testing log_info:")
    log_info("All systems go.")

    print("Testing log_warn:")
    log_warn("Careful...")

    print("Testing log_error:")
    log_error("Crisis mode engaged.")
    
    assert os.path.exists("logs/test_logthis.log"), "Le fichier log n'a pas été créé."
    with open("logs/test_logthis.log", "r", encoding="utf-8") as f:
        content = f.read()
        assert "[INFO] Test INFO log" in content
        assert "[WARN] Test WARN log" in content
        assert "[ERROR] Test ERROR log" in content
    
if __name__ == "__main__":
    test_log_functions()
    print("All tests passed.")