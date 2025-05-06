# Talem CLI Tool

This CLI tooling allows for the addition of more context to be used by Talem AI chatbot.

## Usage (very simple):

```bash
pip install talemai
talemai
```
## Technologies used:

- Click (to build a beautiful CLI)
- PyPDF (to load and read the pdf documents)
- Request (to load online resources to lead. **beware of copyright**)
- Langchain (to convert the pdfs into vector embeddings)
- AstraDB (to store the new vector embeddings)
- Pyfiglet (to make a fashionable and large title greeting)
- Setuptools (allows to config project to be a module in pip)
- Twine (CLI tool used to upload onto pip registry)

## Commit Guide:

To commit properly in this project, you must update the verison of the package in `setup.py`. If you do not, the build command run by Github Actions will fail and the changes will not be pushed to the Pip registry. You will know this is the case if you get the following error:

![image](https://github.com/user-attachments/assets/5d6af954-c848-4647-8c47-6168e93462d8)
