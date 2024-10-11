import sys
from app import app

if __name__ == "__main__":
    port = 5000 
    if "-p" in sys.argv:
        port_index = sys.argv.index("-p") + 1
        if port_index < len(sys.argv):
            port = int(sys.argv[port_index])
    
    app.run(host="0.0.0.0", port=port)
