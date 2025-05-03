from abc import abstractmethod, ABC
from typing import Any, Optional

from PySide6.QtGui import QAction, Qt, QActionGroup
from PySide6.QtWidgets import QToolBar, QMainWindow, QDockWidget, QWidget, QPushButton, QMenu, QMenuBar, QHBoxLayout, \
    QVBoxLayout

from qtlizlib.domain.menuActionTool import InstanceData, InstanceType, ToolbarWidgetType, ToolbarItem, ActionItem, \
    ActionGroupItem, ActionSignalType
from qtlizlib.domain.theme import AppTheme
from qtlizlib.util.menuActionTool import create_toolbar, create_action, create_action_group, create_action_toggle_dock
from qtlizlib.util.qtlizLogger import logger




class ToolbarHandler:

    def __init__(
            self,
            item: ToolbarItem,
            enable_logs: bool = False,
    ):
        self.item: ToolbarItem = item
        self.toolbar: QToolBar | None = None
        self.created = False
        self.enable_logs = enable_logs

    def create(
            self,
            parent: QMainWindow | QDockWidget | QWidget,
            layout: QHBoxLayout | QVBoxLayout | None = None
    ):
        self.toolbar = create_toolbar(self.item, parent)
        if layout is None:
            parent.addToolBar(Qt.ToolBarArea.TopToolBarArea, self.toolbar)
        else:
            layout.addWidget(self.toolbar)
        self.created = True
        logger.debug(f"Toolbar created for {self.item.id}") if self.enable_logs else None

    def destroy(self, parent: QMainWindow | QDockWidget | QWidget, layout: QHBoxLayout | QVBoxLayout | None = None):
        if self.toolbar:
            if layout is None:
                parent.removeToolBar(self.toolbar)
            else:
                layout.removeWidget(self.toolbar)
            self.toolbar.deleteLater()
            self.toolbar = None
            self.created = False
            logger.debug(f"Toolbar destroyed for {self.item.id}") if self.enable_logs else None
        else:
            logger.error("Cannot destroy toolbar %s. Toolbar is not created.", self.item.id)

    def is_created(self) -> bool:
        return self.toolbar is not None and self.created

    def add_action(self, action: QAction):
        if self.is_created():
            self.toolbar.addAction(action)
            logger.debug("Added action %s to toolbar %s", action.objectName(), self.item.id) if self.enable_logs else None
        else:
            logger.error("Cannot add action to toolbar %s. Toolbar is not created.", self.item.id)

    def add_separator(self):
        if self.is_created():
            self.toolbar.addSeparator()
            logger.debug("Added separator to toolbar %s", self.item.id) if self.enable_logs else None
        else:
            logger.error("Cannot add separator to toolbar %s. Toolbar is not created.", self.item.id)

    def add_action_button(self, action: QAction):
        if self.is_created():
            btn = QPushButton(action.text())
            self.toolbar.addWidget(btn)
            logger.debug("Added button %s to toolbar %s", action.objectName(), self.item.id) if self.enable_logs else None
        else:
            logger.error("Cannot add button to toolbar %s. Toolbar is not created.", self.item.id)





class Instance(ABC):

    def __init__(self, inst_type: InstanceType, data: InstanceData):
        self.order = data.order
        self.family = data.family
        self.settings = data.settings
        self.type = inst_type
        self.menu_installed: bool = False
        self.toolbar_installed: bool = False

    @abstractmethod
    def menu_install(self, menu: QMenu):
        pass

    @abstractmethod
    def menu_uninstall(self, menu: QMenu):
        pass

    @abstractmethod
    def toolbar_install(self, toolbar_handler: Optional[ToolbarHandler]):
        pass

    @abstractmethod
    def toolbar_uninstall(self, toolbar_handler: Optional[ToolbarHandler]):
        pass

    def handle_tlb_action_adding(self, toolbar_handler: ToolbarHandler, action: QAction):
        if self.settings.toolbar_widget_type == ToolbarWidgetType.ACTION:
            toolbar_handler.add_action(action)
        elif self.settings.toolbar_widget_type == ToolbarWidgetType.BUTTON:
            toolbar_handler.add_action_button(action)

    def handle_tlb_action_removal(self, toolbar_handler: ToolbarHandler, action: QAction):
        if self.settings.toolbar_widget_type == ToolbarWidgetType.ACTION:
            toolbar_handler.toolbar.removeAction(action)
        elif self.settings.toolbar_widget_type == ToolbarWidgetType.BUTTON:
            for btn_action in toolbar_handler.toolbar.actions():
                if btn_action.text() == action.text():
                    toolbar_handler.toolbar.removeAction(btn_action)


class InstanceAction(Instance):

    def __init__(
            self,
            action: QAction,
            data: InstanceData,
            enable_logs: bool = False,
    ):
        super().__init__(InstanceType.ACTION, data)
        self.action = action
        self.enable_logs = enable_logs

    def menu_install(self, menu: QMenu):
        if self.settings.menu_add:
            logger.debug("Installing action %s to menu %s", self.action.objectName(), menu.title()) if self.enable_logs else None
            menu.addAction(self.action)
            self.menu_installed = True

    def menu_uninstall(self, menu: QMenu):
        if self.settings.menu_add:
            logger.debug("Uninstalling action %s from menu %s", self.action.objectName(), menu.title()) if self.enable_logs else None
            menu.removeAction(self.action)
            self.menu_installed = False

    def toolbar_install(self, toolbar_handler: Optional[ToolbarHandler]):
        if self.settings.toolbar_add and toolbar_handler:
            logger.debug("Installing action %s to toolbar %s", self.action.objectName(), toolbar_handler.item.id) if self.enable_logs else None
            self.handle_tlb_action_adding(toolbar_handler, self.action)

    def toolbar_uninstall(self, toolbar_handler: Optional[ToolbarHandler]):
        if self.settings.toolbar_add and toolbar_handler:
            self.handle_tlb_action_removal(toolbar_handler, self.action)


class InstanceActionGroupInnerMenu(Instance):
    def __init__(
            self,
            inner_menu: QMenu,
            action_group: QActionGroup,
            data: InstanceData,
    ):
        super().__init__(InstanceType.ACTION_GROUP_INNER_MENU, data)
        self.action_group = action_group
        self.inner_menu = inner_menu

    def get_action_from_group(self, action_id: str) -> QAction | None:
        for action in self.action_group.actions():
            if action.objectName() == action_id:
                return action
        return None

    def add_action_to_group(self, action: QAction):
        if action not in self.action_group.actions():
            self.action_group.addAction(action)
        else:
            logger.warning("Action %s already in group %s", action.text(), self.action_group.objectName())

    def remove_action_from_group(self, action: QAction):
        if action in self.action_group.actions():
            self.action_group.removeAction(action)
        else:
            logger.warning("Action %s not in group %s", action.text(), self.action_group.objectName())

    def remove_action_from_group_2(self, action_id: str):
        action = self.get_action_from_group(action_id)
        if action:
            self.action_group.removeAction(action)
        else:
            logger.warning("Action %s not in group %s", action_id, self.action_group.objectName())

    def menu_install(self, menu: QMenu):
        if self.settings.menu_add:
            self.inner_menu.addActions(self.action_group.actions())
            print("sadas")
            menu.addMenu(self.inner_menu)

    def menu_uninstall(self, menu: QMenu):
        if self.settings.menu_add:
            menu.removeAction(self.inner_menu.menuAction())
            self.inner_menu.clear()

    def toolbar_install(self, toolbar_handler: Optional[ToolbarHandler]):
        if self.settings.toolbar_add and toolbar_handler:
            for action in self.action_group.actions():
                self.handle_tlb_action_adding(toolbar_handler, action)

    def toolbar_uninstall(self, toolbar_handler: Optional[ToolbarHandler]):
        if self.settings.toolbar_add and toolbar_handler:
            for action in self.action_group.actions():
                self.handle_tlb_action_removal(toolbar_handler, action)


class InstanceActionGroupParentMenu(Instance):
    def __init__(
            self,
            action_group: QActionGroup,
            data: InstanceData,
    ):
        super().__init__(InstanceType.ACTION_GROUP_PARENT_MENU, data)
        self.action_group = action_group

    def menu_install(self, menu: QMenu):
        if self.settings.menu_add:
            menu.addActions(self.action_group.actions())

    def menu_uninstall(self, menu: QMenu):
        if self.settings.menu_add:
            for action in self.action_group.actions():
                menu.removeAction(action)

    def toolbar_install(self, toolbar_handler: Optional[ToolbarHandler]):
        if self.settings.toolbar_add and toolbar_handler:
            for action in self.action_group.actions():
                self.handle_tlb_action_adding(toolbar_handler, action)

    def toolbar_uninstall(self, toolbar_handler: Optional[ToolbarHandler]):
        if self.settings.toolbar_add and toolbar_handler:
            for action in self.action_group.actions():
                self.handle_tlb_action_removal(toolbar_handler, action)



class InstanceSeparator(Instance):
    def __init__(
            self,
            data: InstanceData,
    ):
        super().__init__(InstanceType.SEPARATOR, data)

    def menu_install(self, menu: QMenu):
        if self.settings.menu_add:
            menu.addSeparator()

    def menu_uninstall(self, menu: QMenu):
        if self.settings.menu_add:
            pass

    def toolbar_install(self, toolbar_handler: Optional[ToolbarHandler]):
        if self.settings.toolbar_add and toolbar_handler:
            toolbar_handler.add_separator()

    def toolbar_uninstall(self, toolbar_handler: Optional[ToolbarHandler]):
        pass



class MenuMasterHandler:

    def __init__(
            self,
            menu: QMenu,
            menu_bar: QMenuBar,
            parent: Any,
            theme: AppTheme,
            toolbar_handler: ToolbarHandler | None = None,
            enable_logs: bool = False,
    ):
        self.parent = parent
        self.menu: QMenu = menu
        self.toolbar_handler = toolbar_handler
        self.menu_bar = menu_bar
        self.enable_logs = enable_logs
        self.theme = theme

        self.index_order = 0
        self.menu_installed = False
        self.toolbar_installed = False

        self.inst_actions: list[InstanceAction] = []
        self.inst_group_menu_inner: list[InstanceActionGroupInnerMenu] = []
        self.action_groups_menu_parent: list[InstanceActionGroupParentMenu] = []
        self.separators: list[InstanceSeparator] = []


    def __is_menu_added(self):
        return self.menu in self.menu_bar.findChildren(QMenu)

    def __is_toolbar_available(self) -> bool:
        return self.toolbar_handler is not None

    def install_menu(self):
        if not self.__is_menu_added():
            self.menu_bar.addMenu(self.menu)
        self.menu_installed = True

    def uninstall_menu(self):
        if self.__is_menu_added():
            self.menu_bar.removeAction(self.menu.menuAction())
        self.menu_installed = False

    def set_toolbar_handler(self, toolbar_handler: ToolbarHandler):
        if self.__is_toolbar_available():
            logger.error("Cannot add toolbar handler %s. Toolbar handler is already set.", toolbar_handler.item.id)
            return
        self.toolbar_handler = toolbar_handler

    def clear_toolbar_handler(self):
        if not self.__is_toolbar_available():
            logger.error("Cannot clear toolbar handler %s. Toolbar handler is not set.", self.toolbar_handler.item.id)
            return
        self.toolbar_handler = None

    def install_toolbar(
            self,
            parent: QMainWindow | QDockWidget | QWidget | None = None,
            layout: QHBoxLayout | QVBoxLayout | None = None
    ):
        if self.__is_toolbar_available():
            parent_to_use = parent if parent else self.parent
            self.toolbar_handler.create(parent_to_use, layout)
            self.toolbar_installed = True
        else:
            logger.error("Cannot install toolbar %s. Toolbar is not available.", self.toolbar_handler.item.id)

    def uninstall_toolbar(self):
        if self.__is_toolbar_available():
            self.toolbar_handler.destroy(self.parent)
            self.toolbar_installed = False
        else:
            logger.error("Cannot uninstall toolbar %s. Toolbar is not available.", self.toolbar_handler.item.id)

    def __get_toolbar_icon_size(self) -> int:
        if self.__is_toolbar_available():
            return self.toolbar_handler.item.icon_size
        return 32

    def __get_installed_actions(self, menu=None) -> list[QAction]:
        if menu is None:
            menu = self.menu
        all_actions = []
        for action in menu.actions():
            all_actions.append(action)
            submenu = action.menu()
            if submenu:
                all_actions.extend(self.__get_installed_actions(submenu))
        return all_actions

    def reinstall_actions(self):
        if not self.menu_installed:
            logger.error("Cannot reinstall actions. Menu is not installed.")
            return
        for instance in self.inst_actions:
            instance.menu_uninstall(self.menu)
            instance.toolbar_uninstall(self.toolbar_handler)
            instance.menu_install(self.menu)
            instance.toolbar_install(self.toolbar_handler)

    def reinstall_action_groups(self, inner: bool = True, parent: bool = True):
        if not self.menu_installed:
            logger.error("Cannot reinstall action groups. Menu is not installed.")
            return
        if inner:
            for instance in self.inst_group_menu_inner:
                instance.menu_uninstall(self.menu)
                instance.toolbar_uninstall(self.toolbar_handler)
                instance.menu_install(self.menu)
                instance.toolbar_install(self.toolbar_handler)
        if parent:
            for instance in self.action_groups_menu_parent:
                instance.menu_uninstall(self.menu)
                instance.toolbar_uninstall(self.toolbar_handler)
                instance.menu_install(self.menu)
                instance.toolbar_install(self.toolbar_handler)

    def reinstall_all(self):
        if not self.menu_installed:
            logger.error("Cannot reinstall all. Menu is not installed.")
            return
        self.reinstall_actions()
        self.reinstall_action_groups(inner=True, parent=True)


    def install_action(
            self,
            item: ActionItem,
            signal: Any | None = None,
            callback: Any | None = None,
            data: InstanceData = InstanceData(),
    ):
        if not self.menu_installed:
            logger.error("Cannot install action %s. Menu is not installed.", item.id)
            return
        action = create_action(
            item=item,
            parent=self.parent,
            signal=signal,
            theme=self.theme,
            callback=callback,
            toolbar_icon_size=self.__get_toolbar_icon_size()
        )
        instance = InstanceAction(action, data)
        self.inst_actions.append(instance)
        instance.menu_install(self.menu)
        instance.toolbar_install(self.toolbar_handler)

    def install_action_group_inner(
            self,
            inner_menu: QMenu,
            item: ActionGroupItem,
            signal: Any | None = None,
            signal_type: ActionSignalType = ActionSignalType.ACTION_OBJECT,
            use_text_for_group: bool = True,
            data: InstanceData = InstanceData(),
    ):
        if not self.menu_installed:
            logger.error("Cannot install action group %s. Menu is not installed.", item.id)
            return
        group = create_action_group(item, self.parent, signal, use_text_for_group=use_text_for_group, signal_type=signal_type)
        instance = InstanceActionGroupInnerMenu(inner_menu, group, data)
        self.inst_group_menu_inner.append(instance)
        instance.menu_install(self.menu)
        instance.toolbar_install(self.toolbar_handler)

    def install_action_group_parent(
            self,
            item: ActionGroupItem,
            signal: Any | None = None,
            signal_type: ActionSignalType = ActionSignalType.ACTION_OBJECT,
            use_text_for_group: bool = True,
            data: InstanceData = InstanceData(),
    ):
        if not self.menu_installed:
            logger.error("Cannot install action group %s. Menu is not installed.", item.id)
            return
        group = create_action_group(
            item=item,
            parent=self.parent,
            theme=self.theme,
            signal=signal,
            use_text_for_group=use_text_for_group,
            signal_type=signal_type
        )
        instance = InstanceActionGroupParentMenu(group, data)
        self.action_groups_menu_parent.append(instance)
        instance.menu_install(self.menu)
        instance.toolbar_install(self.toolbar_handler)

    def append_action_group_inner(self, action: QAction, inner_menu: QMenu):
        if not self.menu_installed:
            logger.error("Cannot append action group %s. Menu is not installed.", action.objectName())
            return
        for instance in self.inst_group_menu_inner:
            if instance.inner_menu == inner_menu:
                instance.add_action_to_group(action)
                instance.menu_uninstall(self.menu)
                instance.toolbar_uninstall(self.toolbar_handler)
                instance.toolbar_install(self.toolbar_handler)
                instance.menu_install(self.menu)
                break

    def append_dock_show_action_menu(self, item: ActionItem, dock: QDockWidget, inner_menu: QMenu | None = None):
        if not self.menu_installed:
            logger.error("Cannot append action %s. Menu is not installed.", item.id)
            return
        action = create_action_toggle_dock(item, dock)
        if inner_menu:
            self.append_action_group_inner(action, inner_menu)

    def remove_dock_show_action_menu(self, item: ActionItem, dock: QDockWidget, inner_menu: QMenu | None = None):
        if not self.menu_installed:
            logger.error("Cannot remove action %s. Menu is not installed.", item.id)
            return
        if inner_menu:
            for instance in self.inst_group_menu_inner:
                if instance.inner_menu == inner_menu:
                    instance.remove_action_from_group_2(item.id)
                    instance.menu_uninstall(self.menu)
                    instance.toolbar_uninstall(self.toolbar_handler)
                    instance.toolbar_install(self.toolbar_handler)
                    instance.menu_install(self.menu)
                    break

    def remove_action_from_group_inner(self, item: ActionItem, inner_menu: QMenu):
        if not self.menu_installed:
            logger.error("Cannot remove action %s. Menu is not installed.", item.id)
            return
        for instance in self.inst_group_menu_inner:
            if instance.inner_menu == inner_menu:
                action = instance.get_action_from_group(item.id)
                if action:
                    instance.remove_action_from_group(action)
                    instance.menu_uninstall(self.menu)
                    instance.toolbar_uninstall(self.toolbar_handler)
                    instance.toolbar_install(self.toolbar_handler)
                    instance.menu_install(self.menu)
                break

    def uninstall_action(self, item: ActionItem):
        if not self.menu_installed:
            logger.error("Cannot uninstall action %s. Menu is not installed.", item.id)
            return
        for instance in self.inst_actions:
            if instance.action.objectName() == item.id:
                instance.menu_uninstall(self.menu)
                instance.toolbar_uninstall(self.toolbar_handler)
                self.inst_actions.remove(instance)
                break

    def uninstall_action_group_inner(self, item: ActionGroupItem):
        if not self.menu_installed:
            logger.error("Cannot uninstall action group %s. Menu is not installed.", item.id)
            return
        for instance in self.inst_group_menu_inner:
            if instance.action_group.objectName() == item.id:
                instance.menu_uninstall(self.menu)
                instance.toolbar_uninstall(self.toolbar_handler)
                self.inst_group_menu_inner.remove(instance)
                break

    def uninstall_action_group_parent(self, item: ActionGroupItem):
        if not self.menu_installed:
            logger.error("Cannot uninstall action group %s. Menu is not installed.", item.id)
            return
        for instance in self.action_groups_menu_parent:
            if instance.action_group.objectName() == item.id:
                instance.menu_uninstall(self.menu)
                instance.toolbar_uninstall(self.toolbar_handler)
                self.action_groups_menu_parent.remove(instance)
                break

    def update_action(
            self,
            action_id: str,
            text: str | None = None,
            status: bool | None = None,
            trigger: Any | None = None,
    ):
        for action in self.__get_installed_actions():
            if action.objectName() == action_id:
                if text is not None:
                    logger.debug("Updating text of action \"%s\" to \"%s\"", action_id, text) if self.enable_logs else None
                    action.setText(text)
                if status is not None:
                    logger.debug("Updating status of action \"%s\" to \"%s\"", action_id, status) if self.enable_logs else None
                    action.setEnabled(status)
                if trigger is not None:
                    logger.debug("Updating trigger of action \"%s\"", action_id) if self.enable_logs else None
                    action.triggered.connect(trigger)
