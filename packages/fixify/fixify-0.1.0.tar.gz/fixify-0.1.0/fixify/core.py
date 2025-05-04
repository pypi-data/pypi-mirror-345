from IPython.display import Code
import requests

class CodeFixer:
    def __init__(self, api_key):
        self.api_key = api_key
        self.url = "https://api.together.xyz/v1/completions"
    
    def fix_code(self, buggy_code):

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        prompt = f"""If no error then dont give output anything just return whole code same as it is [INST] Fix ONLY syntax errors in this Python code. Make MINIMAL changes. Then return Whole Code
ACTUAL CODE TO FIX:
{buggy_code}
[/INST]
Corrected code:"""

        payload = {
            "model": "meta-llama/Llama-4-Maverick-17B-128E-Instruct-FP8",
            "prompt": prompt,
            "max_tokens": 512,
            "temperature": 0.1,
            "top_p": 0.25,
            "stop": ["\n\n", "[/INST]"]
        }

        response = requests.post(self.url, json=payload, headers=headers)


        # Handle API errors
        if response.status_code != 200:
            raise Exception(f"API Error: {response.status_code} — {response.text}")

        data = response.json()
        if 'choices' not in data:
            raise Exception(f"Invalid response format: {data}")

        return self._clean_output(data['choices'][0]['text'])

    def _clean_output(self, text):
        if '```python' in text:
            return text.split('```python')[1].split('```')[0].strip()
        return text.split('Corrected code:')[-1].strip()

class templates:
  def __init__(self, apiToken):
    """
    This class contains methods for interacting with the Together API.

    Parameters:
    apiToken (str): The API token for the Together API.
    """

    self.apiToken = apiToken

  
  def setLLM(self, msg, model="gemini-2.0-flash-lite", edit=False, version = "lite"):
    """
    Uses Gemini HTTP API to generate a response.

    Parameters:
    msg (str): The input prompt.
    model (str): Default is 'gemini-2.0-flash'.
    edit (bool): If True, modifies prompt for code-only output.
    version (str): Default is 'lite'.

    Returns:
    str: Gemini's response text.
    """
    import requests
    import json
    if (version == "lite"):
      model = "gemini-2.0-flash-lite"
    else:
      model = "gemini-2.0-flash"

    if edit:
        msg += "\nJust give code, nothing else. Just clean, plain code."

    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={self.apiToken}"
    headers = {"Content-Type": "application/json"}
    data = {
        "contents": [{
            "parts": [{"text": msg}]
        }]
    }

    try:
        res = requests.post(url, headers=headers, data=json.dumps(data))
        res.raise_for_status()
        return res.json()["candidates"][0]["content"]["parts"][0]["text"]
    except Exception as e:
        print("⚠️ Gemini API error:", str(e))
        return

 
class fixify:
  def __init__(self):
    """
    This class contains methods for interacting with the Together API.
    """
    from dotenv import load_dotenv
    load_dotenv()
  


  def setApi(self):
        
        import os

        # If no environment variable found, check if it's saved locally in a file
        if os.path.exists("api_token.txt"):
          with open("api_token.txt", "r") as file:
            apiToken = file.read().strip()
          return apiToken

        # If no API token found in both places, prompt the user for it
        print("Do You Have API Token (y/n)?")
        flag = input()

        if flag.lower() == "y":
          apiToken = input("Please paste your API token here: ")
          with open("api_token.txt", "w") as file:
            file.write(apiToken)
          print("API Token saved for future use.")
        else:
          print("Go to https://aistudio.google.com/apikey and generate your token. IT'S FREE!!")
          print("Then paste it here:")
          apiToken = input()  # Get the API token from the user
          with open("api_token.txt", "w") as file:
            file.write(apiToken)
          print("API Token saved for future use.")

        return apiToken
  
  def setTogetherAPI(self):
    
    import os
    # If no environment variable found, check if it's saved locally in a file
    if os.path.exists("apiToken.txt"):
      with open("apiToken.txt", "r") as file:
        apiToken = file.read().strip()
      return apiToken

    # If no API token found in both places, prompt the user for it
    print("Do You Have API Token (y/n)?")
    flag = input()

    if flag.lower() == "y":
      apiToken = input("Please paste your API token here: ")
      with open("apiToken.txt", "w") as file:
        file.write(apiToken)
      print("API Token saved for future use.")
    else:
      print("Go to https://api.together.ai/ and generate your token. IT'S FREE!!")
      print("Then paste it here:")
      apiToken = input()  # Get the API token from the user
      with open("apiToken.txt", "w") as file:
        file.write(apiToken)
      print("API Token saved for future use.")

    return apiToken


  def fixCode(self, code = "null", prompt = "Fix this code", error = "follow the prompt", notebook = False):
    """
    This function is the main entry point for the code fixing functionality. It takes a code block, a prompt, and an error message as input, and returns the fixed code block.

    Parameters:
    code (str): The code block that needs to be fixed. If set to "null", the function will prompt the user for a code block.
    prompt (str): The prompt given by the user for the code block.
    error (str): The error message given by the user for the code block.
    notebook (bool): If set to True, the function will use a Jupyter notebook style output.

    Returns:
    str: The fixed code block.
    """
    if (code == "null"):
      print("Please paste your code here:")
      return
    past_prompts = self.getLastEntries("memory.txt", 50)
    msg = f"""
    You are an assistant with access to previous interactions (last 100 entries):

    {past_prompts}

    The user now asks:

    {prompt} and {code}

    Instructions:
    - Respond concisely and clearly, breaking lines appropriately (avoid long single lines).
    - Do NOT repeat or mention previous prompts unless the user explicitly asks.
    - Stay focused on the current question and avoid unnecessary explanation.
    - Output ONLY the fixed code.
    - Format it properly with indentation and line breaks.
    - Start with: ```python
    - End with: ```
    - DO NOT include extra text, comments, or inline outputs.
    - DO NOT use one-line format like: ```python def func(): print("...") ```
      """




    template = templates(self.setApi())
    ai_output = template.setLLM(msg)



    msg = f"""
    This was the original prompt from the user:
    {prompt}

    The AI made the following changes to the code:
    {code}

    Here is the updated output:
    {ai_output}

    Now, generate a concise summary of the changes made in the code.
    Instructions:
    - Do NOT include the code itself.
    - Explain what was fixed, improved, or modified.
    - Break your explanation into readable lines (avoid long continuous lines).
    """


    template = templates(self.setApi())
    second_ai_output = template.setLLM(msg)


    userInput = code + prompt
    aiOutput = ai_output + second_ai_output
    self.send_to_memory(userInput, aiOutput, error)
    # Display the output
    from IPython.display import Markdown, display
    if (notebook):
      display(Markdown(f"### 🔴 Older Code\n```python\n{code}\n```"))
      display(Markdown(f"### 🟢 Corrected Code\n```python\n{ai_output.strip('`python').strip('`')}\n```"))
      display(Markdown(f"### 📝 Summary of Changes\n{second_ai_output}"))
    else:
      print(f"### 🔴 Older Code\n```python\n{code}\n```")
      print(f"### 🟢 Corrected Code\n```python\n{ai_output.strip('`python').strip('`')}\n```")
      print(f"### 📝 Summary of Changes\n{second_ai_output}")


  def send_to_memory(self, userInput, aiOutput, error):
    """
    This function is used to send the user input and AI output to the memory.txt file.

    Parameters:
    userInput (str): The code block that needs to be fixed.
    aiOutput (str): The fixed code block.
    error (str): The error message given by the user for the code block.
    """

    msg_for_ur_aiOutput = f"""
    This is content from user which is {aiOutput} summarize this into one to two lines and keep the code as it as dont change it
    """

    template = templates(self.setApi())
    ai_response = template.setLLM(msg_for_ur_aiOutput)
    self.save_to_memory(userInput, ai_response, error)

  def common_upper_part_of_method(self, code):
    if (code == "null"):
      print("Please paste your code here:")
      return




  def explainFixes(self, code = "null",error = "follow the prompt", prompt = "Fix this code", notebook = False, model = "llama-4"):
    """
    This function is used to explain the fixes to the user.

    Parameters:
    code (str): The code block that needs to be fixed.
    error (str): The error message given by the user for the code block.
    prompt (str): The prompt given by the user for the code block.
    notebook (bool): If set to True, the function will use a Jupyter notebook style output.
    """
    self.common_upper_part_of_method(code = code)

    past_prompts = self.getLastEntries("memory.txt", 50)

    msg = f"""
    You are a powerful debugging assistant with access to the last 50 code interactions:

    {past_prompts}

    The user now provides:

    Prompt:
    {prompt}

    Code:
    {code}

    error:
    {error}

    Instructions:
    - Analyze the code line-by-line and identify all logical, syntactic, and runtime errors.
    - For **each problematic line**, rewrite it and add a comment at the end: <--- "Explanation of what's wrong"
    - DO NOT provide the full corrected code.
    - If a fix is needed, show **only the corrected version of the problematic line below the original**.
    - Use proper indentation and formatting.
    - Highlight only the incorrect lines, leave others untouched.
    - Start the output with: ```python
    - End with: ```
    - DO NOT include any summaries, extra explanations, or previous prompts.
    - DO NOT use one-line code blocks like: ```python def func(): print("...") ```
    """

    userInput = code + prompt

    template = templates(self.setApi())

    msg = f"""
    You are a powerful coding assistant with access to the last 100 interactions:

    {past_prompts}

    The user now provides:

    Prompt:
    {prompt}

    Code:
    {code}

    Instructions:
    - Analyze the code and generate a **fully corrected version**.
    - Only fix syntactic, logical, and runtime issues.
    - DO NOT modify working or unrelated parts.
    - Maintain original structure and logic as much as possible.
    - Use clean formatting, indentation, and break long lines if needed.
    - Start with: ```python
    - End with: ```
    - DO NOT include extra text, explanations, or comments unless they're in the original.
    - Output only the final fixed code.
    """

    corrected_code = template.setLLM(msg, model)

    msg = f"""
    You are a code analysis assistant with access to the last 100 entries:

    {past_prompts}

    The user now provides:

    Prompt:
    {prompt}

    Code:
    {code}

    error:
    {error}

    Instructions:
    - Go through the code line by line.
    - For every incorrect line, describe:
        1. What's wrong.
    2. Why it's wrong.
    3. How to fix it.
    - Do not change working lines.
    - Structure your explanation in this format:

    Line X:
    [Original Line]
    Problem: ...
    Fix: ...

    - Do not include summaries or previous prompts.
    - Output only analysis, clean and to the point.
    """

    summary = template.setLLM(msg, model)
    self.send_to_memory(userInput, corrected_code, summary)
    from IPython.display import display, HTML, Markdown

    # Display Original, Corrected Code, and Explanation
    if (notebook == True):
        display(Markdown("### 🔴 Original Code"))
        display(Markdown(f"```python\n{code.strip()}\n```"))

        display(Markdown("### 🟢 Fixed Code"))
        display(Markdown(f"```python\n{corrected_code.strip().strip('`python').strip('`')}\n```"))

        display(Markdown("### 🧠 Line-by-Line Explanation"))
        display(Markdown(f"<pre>{summary.strip()}</pre>"))
    else:
        print("### Original Code")
        print(code.strip())

        print("### Fixed Code")
        print(corrected_code.strip().strip('`python').strip('`'))

        print("### Line-by-Line Explanation")
        print(summary.strip())





  def getLastEntries(self, filename, maxentries):
    """Returns the last MAX_ENTRIES entries from the memory file.

    Parameters
    ----------
    filename : str
        The name of the file to read from.
    maxentries : int
        The number of entries to return.

    Returns
    -------
    str
        The last MAX_ENTRIES lines of the file.
    """

    MEMORY_FILE = filename
    MAX_ENTRIES = maxentries
    from pathlib import Path
    Path(MEMORY_FILE).touch(exist_ok=True)

    past_prompts = ""

    # Read the file and collect previous prompts and responses, limit to MAX_ENTRIES
    with open(MEMORY_FILE, "r") as file:
        lines = file.readlines()
        past_prompts = "".join(lines[-MAX_ENTRIES:])  # Take the last MAX_ENTRIES entries

    return past_prompts


  def heyAI(self, prompt=None, model = "llama-4"):
    """Send a prompt to the AI and get a response back.

    Parameters
    ----------
    prompt : str
        The prompt to send to the AI.
    model : str
        The model to use. Currently supported models are "llama-4" and "llama-7b".

    Returns
    -------
    str
        The AI's response.
    """

    if prompt is None:
        print("Please enter your prompt.")
        return

    import json
    from pathlib import Path
    # Step 1: Read past memory from chatMemory.txt
    MEMORY_FILE = "chatMemory.txt"
    MAX_ENTRIES = 200
    Path(MEMORY_FILE).touch(exist_ok=True)

    past_prompts = self.getLastEntries(MEMORY_FILE, MAX_ENTRIES)

    # Step 2: Combine past prompts with the new prompt
    msg = f"""
    Here's what we talked about earlier (last {MAX_ENTRIES} entries):

    {past_prompts}

    Now, the user asks:

    {prompt}

    Please provide a response based on the context above.
    If the user asks for past context again, refer back to this message.

    Ensure your response is concise, clear, and formatted for readability.
    Don't repeat the past conversation unless explicitly asked.
    keep breaking lines dont cross width of screen
    """



    # Step 3: Send the combined prompt to the AI model
    template = templates(self.setApi())
    ai_output = template.setLLM(msg, model)

    # Step 4: Save new entry to memory
    entry = json.dumps(
        {"user_prompt": prompt, "ai_output": ai_output},
        indent=2
    ) + "\n---\n"

    with open(MEMORY_FILE, "a") as f:
        f.write(entry)

    print(ai_output)







  def save_to_memory(self, user_input, ai_response, error):
    """Save the user's input, AI response, and error to memory.txt.

    Parameters
    ----------
    user_input : str
        The user's input.
    ai_response : str
        The AI's response.
    error : str
        The error message.
    """
    import json
    from pathlib import Path

    MEMORY_FILE = "memory.txt"
    MAX_ENTRIES = 200
    Path(MEMORY_FILE).touch(exist_ok=True)

    # Create entry with proper formatting and separator
    entry = json.dumps(
        {"user": user_input, "ai": ai_response, "what was the error": error},
        indent=2
    ) + "\n---\n"

    with open(MEMORY_FILE, "a") as f:
        f.write(entry)

    # Read and split by separator
    content = Path(MEMORY_FILE).read_text()
    entries = content.strip().split("\n---\n")

    # Trim to last MAX_ENTRIES and rewrite
    trimmed = "\n---\n".join(entries[-MAX_ENTRIES:]) + "\n---\n"
    Path(MEMORY_FILE).write_text(trimmed)


  def clear_memory(self, filepath):
    """Clear the memory file.

    Parameters
    ----------
    filepath : str
        The path to the memory file.
    """
    from pathlib import Path
    Path(filepath).write_text("")
    return "Memory cleared"

  
  def get_method_from_file(self, filepath, start_line, end_line):
    """Get the method from a file.

    Parameters
    ----------
    filepath : str
        The path to the file.
    start_line : int
        The starting line of the method.
    end_line : int
        The ending line of the method.

    Returns
    -------
    str
        The method code.
    """
    with open(filepath, "r") as file:
        lines = file.readlines()

    # Ensure indices are within bounds
    if start_line < 0 or end_line >= len(lines) or start_line > end_line:
        print("Invalid line indices.")
        return None
    
    # Extract lines between start_line and end_line
    method_code = ''.join(lines[start_line:end_line+1])
    return method_code
  
  def get_correct_method_to_edit(self, filepath, start_line, end_line, model = "llama-4", error = "follow the prompt", prompt = "fix the code"):
    """Get the correct method to edit.

    Parameters
    ----------
    filepath : str
        The path to the file.
    start_line : int
        The starting line of the method.
    end_line : int
        The ending line of the method.
    model : str
        The model to use. Currently supported models are "llama-4" and "llama-7b".
    error : str
        The error message.
    prompt : str
        The prompt given by the user for the code block.

    Returns
    -------
    str
        The correct method to edit.
    """
    method_code = self.get_method_from_file(filepath, start_line, end_line)
    apiToken = self.setApi()
    
    msg = f"""
    You are an AI with access to the following code block:
    {method_code}

    your work is {prompt}
    and this is the error {error}
    Your work is just give code as output nothing else
    Just corrected code
    Dont use any ```python just plain format code
    """

    template = templates()
    output = template.setLLM(apiToken, msg, model, edit = True)

    return output
  
  # def fix_code_in_file(self, filepath, start_line, end_line, model = "llama-4", error = "follow the prompt", prompt = "fix the code"):
  #   """Fix the code in a file.

  #   Parameters
  #   ----------
  #   filepath : str
  #       The path to the file.
  #   start_line : int
  #       The starting line of the method.
  #   end_line : int
  #       The ending line of the method.
  #   model : str
  #       The model to use. Currently supported models are "llama-4" and "llama-7b".
  #   error : str
  #       The error message.
  #   prompt : str
  #       The prompt given by the user for the code block.

  #   Returns
  #   -------
  #   None
  #   """
  #   correct_code = self.get_correct_method_to_edit(filepath, start_line, end_line, model, error, prompt)
  #   self.edit_in_file(start_line, end_line, correct_code, filepath)

  # def edit_in_file(self, start_line, end_line, correct_code, filepath):
  #   """Edit the code in a file.

  #   Parameters
  #   ----------
  #   start_line : int
  #       The starting line of the method.
  #   end_line : int
  #       The ending line of the method.
  #   correct_code : str
  #       The correct code to edit.
  #   filepath : str
  #       The path to the file.

  #   Returns
  #   -------
  #   None
  #   """
  #   with open(filepath, "r") as file:
  #       lines = file.readlines()

  #   # Delete the old code block
  #   del lines[start_line:end_line+1]

  #   # Add the corrected code properly line-by-line
  #   corrected_lines = [line + "\n" for line in correct_code.strip().splitlines()]
  #   lines[start_line:start_line] = corrected_lines

  #   # Write the updated lines back to file
  #   with open(filepath, "w") as file:
  #       file.writelines(lines)

    
  
  def explainFromFile(self, filepath, start_line, end_line = None, model = "llama-4", error = "follow the prompt", prompt = "explain the code", size = "short"):
    """Explain the code from a file.

    Parameters
    ----------
    filepath : str
        The path to the file.
    start_line : int
        The starting line of the method.
    end_line : int
        The ending line of the method.
    model : str
        The model to use. Currently supported models are "llama-4" and "llama-7b".
    error : str
        The error message.
    prompt : str
        The prompt given by the user for the code block.
    size : str
        The size of the explanation. Currently supported sizes are "short" and "long".

    Returns
    -------
    None
    """

    if (end_line is None):
      with open(filepath, "r") as file:
          end_line = len(file.readlines()) - 1
    
    method_code = self.get_method_from_file(filepath, start_line, end_line)

    apiToken = self.setApi()
    template = templates(apiToken)
    msg = f"""
    You are an AI with access to the following code block:
    {method_code}

    your work is {prompt}
    and this is the error {error}
    Explain this code what it works how it works
    in {size}
    Dont print ni md format print in plain paragraph but with correct format and break in lines
    """
    output = template.setLLM(msg)
    print(output)

  def return_code_from_file(self, filepath, start_line, end_line):
        method_code = self.get_method_from_file(filepath, start_line, end_line)
        return method_code

  def edit_in_file(self, filepath, start_line=0, end_line=None):
        target_code = self.return_code_from_file(filepath, start_line, end_line)
        return target_code  # ACTUAL FIX: Return the code instead of just printing

  def get_correct_code_to_edit(self, filepath=None, start_line=0, end_line=None):
        if filepath is None:
            print("Enter the filename")
            return

        buggy_code = self.edit_in_file(filepath=filepath, start_line=start_line, end_line=end_line)
        codefix = CodeFixer(self.setTogetherAPI())  # Consider making this configurable
        return codefix.fix_code(buggy_code=buggy_code)

  def now_edit(self, filepath, start_line=0, end_line=None):
        with open(filepath, "r") as file:
            lines = file.readlines()
        
        if end_line is None:
            end_line = len(lines) - 1
        end_line = min(end_line, len(lines)-1)  # Ensure within bounds

        corrected_code = self.get_correct_code_to_edit(
            filepath=filepath, 
            start_line=start_line, 
            end_line=end_line
        )

        # Process corrected code with proper newlines
        corrected_lines = []
        for line in corrected_code.split('\n'):
            corrected_lines.append(f"{line}\n")
        
        # Remove trailing empty line if present
        if corrected_lines and corrected_lines[-1] == "\n":
            corrected_lines.pop()

        # Replace the target section
        lines[start_line : end_line+1] = corrected_lines  # FIXED SLICE

        with open(filepath, "w") as file:
            file.writelines(lines)
        return "#Done"



