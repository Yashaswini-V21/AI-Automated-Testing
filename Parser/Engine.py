import re
from langgraph.graph import StateGraph, END
from typing import TypedDict

class InstructionParser:

    VERB_MAP = {
        "goto": ["go to", "open", "visit", "navigate"],
        "click": ["click", "press", "tap", "hit"],
        "fill": ["enter", "type", "fill", "write"],
        "assert": ["verify", "assert", "ensure", "confirm"],
    }

    SELECTOR_KEYWORDS = {
        "username": "#username",
        "email": "#email",
        "password": "#password",
        "login": "#login",
        "submit": "button[type='submit']",
    }

    def normalize(self, text):
        text = text.lower()
        text = text.replace(",", " ")
        # text = text.replace(".", " ")
        return text.strip()

    def detect_action(self, chunk):
        for action, verbs in self.VERB_MAP.items():
            for v in verbs:
                if v in chunk:
                    return action
        return "unknown"

    def extract_selector(self, chunk):
        for key, sel in self.SELECTOR_KEYWORDS.items():
            if key in chunk:
                return sel
        return None  # ambiguous

    def extract_value(self, chunk):
        match = re.search(r'\"(.*?)\"', chunk)
        if match:
            return match.group(1)
        return None

    def extract_url(self, chunk):
        if "/login" in chunk:
            return "/login"
        if "/signup" in chunk:
            return "/signup"   
        match = re.search(r'\b((?:https?://|www\.)?[a-zA-Z0-9-]+\.[a-zA-Z]{2,}(?:/[^\s]*)?)', chunk)
        if match:
            return match.group(0)
        return None

    def validate_and_fix(self, action_dict):
        """ Add fallback values to avoid crashes """
        if action_dict["action"] == "goto":
            if not action_dict.get("url"):
                action_dict["url"] = "/"

        if action_dict["action"] in ["click", "fill"]:
            if not action_dict.get("selector"):
                action_dict["selector"] = "body"

        if action_dict["action"] == "fill":
            if not action_dict.get("value"):
                action_dict["value"] = ""

        return action_dict

    def parse(self, instruction):
        instruction = self.normalize(instruction)
        chunks = re.split(r'and|then|after that|,', instruction)

        parsed_actions = []

        for chunk in chunks:
            chunk = chunk.strip()
            if not chunk:
                continue

            action = self.detect_action(chunk)
            selector = self.extract_selector(chunk)
            value = self.extract_value(chunk)
            url = self.extract_url(chunk)

            action_dict = {"action": action}

            if action == "goto":
                action_dict["url"] = url
            elif action == "click":
                action_dict["selector"] = selector
            elif action == "fill":
                action_dict["selector"] = selector
                action_dict["value"] = value
            else:
                action_dict["note"] = "Ambiguous or unknown instruction"

            validated = self.validate_and_fix(action_dict)
            parsed_actions.append(validated)

        return parsed_actions

# def dummy_code_generator(state):
#     return {"result": f"Actions received: {state['parsed']}"}

class AgentState(TypedDict, total=False):
    input: str
    parsed: list
    result: str


parser = InstructionParser()

def parser_node(state: AgentState):
    text = state.get("input", "")
    parsed = parser.parse(text)
    if len(parsed)==0:
        state["parsed"]=0
    else:
        state["parsed"] = parsed
    return state

def generator_node(state: AgentState):

    if state["parsed"]==0:
        state["result"]=0
    else:
        state["result"] = f"genrator received: {state['parsed']}"
    return state


from langgraph.graph import StateGraph, END

workflow = StateGraph(AgentState)

workflow.add_node("parser", parser_node)
workflow.add_node("codegen", generator_node)

workflow.set_entry_point("parser")
workflow.add_edge("parser", "codegen")
workflow.add_edge("codegen", END)

app = workflow.compile()