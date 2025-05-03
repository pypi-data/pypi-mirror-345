from pathlib import Path
from typing import Any, Callable

from PySide6.QtCore import QSize
from PySide6.QtGui import QAction, QActionGroup, Qt
from PySide6.QtWidgets import QToolBar, QDockWidget, QPushButton

from qtlizlib.domain.menuActionTool import ToolbarItem, ActionItem, ActionGroupItem, ActionSignalType
from qtlizlib.domain.theme import AppTheme
from qtlizlib.handler.resource import ResHandler


def create_toolbar(item: ToolbarItem, parent: Any) -> QToolBar:
    toolbar = QToolBar(parent)
    toolbar.setObjectName(item.id)
    toolbar.setIconSize(QSize(item.icon_size, item.icon_size))
    toolbar.setWindowTitle(item.name)
    toolbar.setOrientation(item.orientation)
    toolbar.setMovable(item.movable)
    return toolbar


def create_action(
        item: ActionItem,
        parent: Any,
        theme: AppTheme,
        signal: Any | None = None,
        callback: Callable | None = None,
        use_text_for_group: bool = False,
        toolbar_icon_size: int = 32,
) -> QAction:
    action = QAction(parent)
    action.setObjectName(item.id)
    if use_text_for_group:
        action.setText(item.text_for_group)
    else:
        action.setText(item.text)
    if item.icon_res:
        icon = ResHandler.get_icon(item.icon_res, theme, False, toolbar_icon_size)
        action.setIcon(icon)
    if item.shortcut:
        action.setShortcut(item.shortcut)
    if item.menu_role:
        action.setMenuRole(item.menu_role)
    action.setEnabled(item.enabled)
    action.setVisible(item.visible)
    action.setCheckable(item.checkable)
    action.setChecked(item.checked)
    if signal:
        action.triggered.connect(signal.emit)
    elif callback:
        action.triggered.connect(callback)
    return action



def create_action_group(
        item: ActionGroupItem,
        parent: Any,
        theme: AppTheme,
        signal: Any | None = None,
        callback: Callable | None = None,
        use_text_for_group: bool = False,
        signal_type: ActionSignalType = ActionSignalType.ACTION_OBJECT,
) -> QActionGroup:
    action_group = QActionGroup(parent)
    action_group.setExclusive(item.exclusive)
    for action in item.actions:
        action_obj = create_action(action, parent, theme, use_text_for_group=use_text_for_group)
        action_group.addAction(action_obj)
    if signal:
        action_group.triggered.connect(signal.emit)
    elif callback:
        action_group.triggered.connect(callback)
    return action_group


def create_action_text_path(path: Path, parent: Any, on_clicked) -> QAction:
    action = QAction(parent)
    action.setText(path.__str__())
    action.setObjectName("action_recent_path_" + path.name)
    action.triggered.connect(on_clicked)
    action.setEnabled(path.exists())
    if path.is_dir():
        action.setStatusTip("Open folder" + path.__str__())
    elif path.is_file():
        action.setStatusTip("Open file" + path.__str__())
    return action


def create_action_contextual(text: str, parent: Any, on_clicked) -> QAction:
    action = QAction(parent)
    action.setText(text)
    action.triggered.connect(on_clicked)
    return action


def create_action_toggle_dock(item: ActionItem, widget: QDockWidget) -> QAction:

    def match_action_dock_shortcut(action: QAction, dock: QDockWidget, shortcut: str | None):
        action.setChecked(dock.isVisible())
        if shortcut is not None:
            action.setShortcut(shortcut)
        def toggle_visibility():
            dock.setVisible(action.isChecked())
        action.toggled.connect(toggle_visibility)
        dock.visibilityChanged.connect(action.setChecked)

    action = QAction(widget)
    action.setObjectName(item.id)
    action.setText(item.text)
    action.setCheckable(True)
    match_action_dock_shortcut(action, widget, item.shortcut)
    return action


def create_action_btn_push(
        item: ActionItem,
        parent: Any,
        signal: Any | None = None,
        callback: Callable | None = None,
) -> QPushButton:
    btn = QPushButton(parent)
    btn.setObjectName(item.id)
    btn.setText(item.text)
    btn.setCheckable(item.checkable)
    btn.setChecked(item.checked)
    btn.setEnabled(item.enabled)
    btn.setVisible(item.visible)
    if signal:
        btn.clicked.connect(signal.emit)
    elif callback:
        btn.clicked.connect(callback)
    return btn