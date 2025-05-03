#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import importlib.util
from typing import Dict, Any

from loguru import logger

from .. import event_bus

class PluginManager:
    def __init__(self, plugin_dir: str):
        self.plugin_dir = plugin_dir
        self.plugins: Dict[str, Any] = {}

    def load_plugins(self):
        if not os.path.exists(self.plugin_dir):
            return

        for fname in os.listdir(self.plugin_dir):
            if fname.endswith(".py") and not fname.startswith("_"):
                self._load_plugin(os.path.join(self.plugin_dir, fname))

    def _load_plugin(self, filepath: str):
        plugin_id = os.path.basename(filepath)[:-3]

        spec = importlib.util.spec_from_file_location(plugin_id, filepath)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)

        plugin_cls = getattr(module, "Plugin", None)
        if not plugin_cls or not callable(plugin_cls):
            return

        plugin = plugin_cls()

        for attr_name in dir(plugin):
            if attr_name.startswith("on_") and len(attr_name) > 3:
                handler = getattr(plugin, attr_name)
                if callable(handler):
                    event_bus.register(attr_name[3:], handler)

        self.plugins[plugin_id] = plugin
