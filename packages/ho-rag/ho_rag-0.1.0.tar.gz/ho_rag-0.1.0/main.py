from server import mcp
from dotenv import load_dotenv
import tools.answer_patient_queries

load_dotenv()

def main():
    mcp.run()

if __name__ == "__main__":
    main()
