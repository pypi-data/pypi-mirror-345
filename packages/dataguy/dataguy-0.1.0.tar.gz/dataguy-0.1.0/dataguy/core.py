import re
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from claudette import Chat, models
from .context_manager import ContextManager

class DataGuy:
    def __init__(self, max_code_history=100):
        self.context = ContextManager(max_code_history=max_code_history)
        self.data = None

        self.chat_code = Chat(self._select_model("code"), sp="You write Python code for pandas and matplotlib tasks.")
        self.chat_text = Chat(self._select_model("text"), sp="You explain datasets and their structure clearly.")
        self.chat_image = Chat(self._select_model("image"), sp="You describe uploaded data visualizations clearly, so plot can be recreated based on that.")

    def _select_model(self, mode):
        if mode == "image":
            return next((m for m in models if "opus" in m), models[-1])
        elif mode == "text":
            return next((m for m in models if "sonnet" in m or "haiku" in m), models[-1])
        else:
            return models[-1]

    def _generate_code(self, task: str) -> str:
        prompt = self.context.get_context_summary() + "\n# Task: " + task
        resp = self.chat_code(prompt)
        raw = resp.content[0].text
        match = re.search(r'```(?:python)?\n(.*?)```', raw, re.S)
        return match.group(1).strip() if match else raw.strip()

    def _exec_code(self, code: str) -> dict:
        print(code)
        ns = {'pd': pd, 'np': np, 'data': self.data, 'plt': plt}
        base = set(ns)
        exec(code, ns)
        self.context.add_code(code)
        self.context.update_from_globals(ns)
        new_keys = set(ns) - base
        return {k: ns[k] for k in new_keys if not k.startswith('__')} | {'data': ns['data']} if 'data' in ns else {}

    def set_data(self, obj):
        if isinstance(obj, pd.DataFrame):
            self.data = obj.copy()
        elif isinstance(obj, (dict, list, np.ndarray)):
            self.data = pd.DataFrame(obj)
        else:
            raise TypeError(f"Unsupported data type: {type(obj)}")
        self.context.update_from_globals(globals())
        return self.data

    def summarize_data(self):
        if self.data is None:
            raise ValueError("No data loaded. Use set_data() first.")
        return {
            'shape': self.data.shape,
            'columns': list(self.data.columns),
            'missing_counts': self.data.isna().sum().to_dict(),
            'means': self.data.mean(numeric_only=True).to_dict()
        }

    def describe_data(self) -> str:
        summary = self.summarize_data()
        prompt = (
            "Describe the dataset in a few sentences based on the following summary:\n"
            f"{summary}"
        )
        resp = self.chat_text(prompt)
        desc = resp.content[0].text
        self.context.add_code(f"# Description: {desc}")
        return desc

    def wrangle_data(self) -> pd.DataFrame:
        if self.data is None:
            raise ValueError("No data loaded. Use set_data() first.")
        summary = self.summarize_data()
        desc = self.describe_data()
        task = (
            "Write a lambda function named `wrangler` that takes a pandas DataFrame and wrangles it for analysis.\n"
            f"Summary: {summary}\n"
            f"Description: {desc}"
        )
        code = self._generate_code(task)
        ns = self._exec_code(code)
        wrangler = ns.get('wrangler')
        if callable(wrangler):
            self.data = wrangler(self.data)
        return self.data

    def analyze_data(self):
        if self.data is None:
            raise ValueError("No data loaded. Use set_data() first.")
        task = "Analyze the pandas DataFrame `data` and return a dict `result` with shape, columns, and descriptive stats."
        code = self._generate_code(task)
        ns = self._exec_code(code)
        return ns.get('result')

    def plot_data(self, column_x: str, column_y: str):
        if self.data is None:
            raise ValueError("No data loaded. Use set_data() first.")
        task = f"Create a scatter plot of `data` with x='{column_x}' and y='{column_y}'. Use matplotlib."
        code = self._generate_code(task)
        self._exec_code(code)

    def describe_plot(self, img_bytes: bytes) -> str:
        resp = self.chat_image([img_bytes, "This plot will be reproduced in python based on your description. Please describe it in detail."])
        desc = resp.content[0].text
        self.context.add_code(f"# Plot description: {desc}")
        return desc

    def recreate_plot(self, plot_description: str):
        if self.data is None:
            raise ValueError("No data loaded. Use set_data() first.")
        # incorporate wrangled summary and dataset description
        summary = self.summarize_data()
        desc = self._data_description or ""
        task = (
            "Write Python code using pandas and matplotlib to create a plot for 'data' similar to the description below. It is a different dataset.\n"
            f"the data is in the variable data_to_plot\n"
            f"Dataset summary: {summary}\n"
            f"Dataset description: {desc}\n"
            f"Plot description: {plot_description}"
        )
        code = self._generate_code(task)
        self._exec_code(code)
