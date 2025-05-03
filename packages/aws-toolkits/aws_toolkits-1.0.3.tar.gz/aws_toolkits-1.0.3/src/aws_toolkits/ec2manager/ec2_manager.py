# -*- coding: utf-8 -*-
# @Time    : 2025/3/18 16:18
# @Author  : YQ Tsui
# @File    : ec2_manager.py
# @Purpose : This file contains the class definition of EC2Manager, which is used to Start or stop EC2 instances.

from functools import lru_cache
from pathlib import Path
from typing import cast

import boto3
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QApplication,
    QMessageBox,
    QPushButton,
    QSizePolicy,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)
from ruamel.yaml import YAML
from .security_group_mgr import SecurityGroupEditor


@lru_cache(maxsize=1)
def load_config() -> dict:
    config_path = Path.home().joinpath(".aws_ec2.yaml")
    if config_path.exists():
        with open(config_path, "r") as f:
            yaml = YAML(typ="safe")
            return yaml.load(f)
    return {}


class CopyableQTableWidget(QTableWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setSelectionBehavior(QTableWidget.SelectItems)
        self.setSelectionMode(QTableWidget.SingleSelection)
        self.verticalHeader().setVisible(False)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_C and (event.modifiers() & Qt.ControlModifier):
            selected_items = self.selectedItems()
            if selected_items:
                clipboard = QApplication.clipboard()
                clipboard.setText(selected_items[0].text())
        else:
            super().keyPressEvent(event)


class EC2Manager(QWidget):

    STATUS_COLORS = {
        "running": "green",
        "stopped": "red",
        "stopping": "red",
    }

    def __init__(self, parent=None):
        super().__init__(parent)
        self._load_config()
        self.init_ui()
        self.waiting_sth = False
        self.security_group_editor = None

    def _load_config(self):
        config = load_config()
        self.load_status_at_start = config.get("load_status_at_start", False)
        instances = config.get("instances", {})
        self.instances = {}
        self.instances_status = {}
        self.authorization_profile = config.get("authorization_profile", "default")
        self.session = boto3.Session(profile_name=self.authorization_profile)
        for region, instances in instances.items():
            for instance in instances:
                instance["region"] = region
            self.instances.update({instance["id"]: instance for instance in instances})
            if self.load_status_at_start:

                ec2_client = self.session.client("ec2", region_name=region)
                response = ec2_client.describe_instances(InstanceIds=list(self.instances.keys()))
                for reservation in response["Reservations"]:
                    for instance in reservation.get("Instances", []):
                        self.instances_status[instance["InstanceId"]] = instance["State"]["Name"]
            else:
                self.instances_status.update({instance_id: "Unknown" for instance_id in self.instances})

    def init_ui(self):
        self.setWindowTitle("EC2 Manager")
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        layout = QVBoxLayout()

        self.reload_instances_btn = QPushButton("Reload Instances")
        self.reload_instances_btn.clicked.connect(self.load_all_available_instances)
        self.instances_table = CopyableQTableWidget()
        self.instances_table.setColumnCount(8)
        self.instances_table.setHorizontalHeaderLabels(
            ["Instance ID", "Region", "Status", "IP Address.", "Start", "Stop", "Security Group", "Edit"]
        )
        self.instances_table.setColumnWidth(3, 150)
        self.refresh_table()
        layout.addWidget(self.reload_instances_btn)
        layout.addWidget(self.instances_table)
        self.setLayout(layout)

        self.adjust_main_widget_width()

    def adjust_main_widget_width(self):
        self.instances_table.resizeColumnsToContents()
        table_width = self.instances_table.horizontalHeader().length()
        self.instances_table.setMinimumWidth(table_width)
        self.adjustSize()

    def refresh_table(self):
        self.instances_table.setRowCount(0)
        self.instances_table.setRowCount(len(self.instances))
        for i, instance in enumerate(self.instances.values()):
            self.instances_table.setItem(i, 0, QTableWidgetItem(instance["id"]))
            self.instances_table.setItem(i, 1, QTableWidgetItem(instance["region"]))
            status_btn = QPushButton()
            self._display_status(status_btn, self.instances_status[instance["id"]])
            status_btn.clicked.connect(self.describe_instance_status)
            self.instances_table.setCellWidget(i, 2, status_btn)
            self.instances_table.setItem(i, 3, QTableWidgetItem("--"))
            start_btn = QPushButton("Start")
            start_btn.clicked.connect(self.start_instance)
            self.instances_table.setCellWidget(i, 4, start_btn)
            stop_btn = QPushButton("Stop")
            stop_btn.clicked.connect(self.stop_instance)
            self.instances_table.setCellWidget(i, 5, stop_btn)
            self.instances_table.setItem(i, 6, QTableWidgetItem(instance["security_group"]))
            edit_btn = QPushButton("Edit")
            edit_btn.clicked.connect(self.edit_security_group)
            self.instances_table.setCellWidget(i, 7, edit_btn)

        self.adjust_main_widget_width()

    def _display_status(self, status_btn: QPushButton, status):
        status_btn.setText(status)
        if status in self.STATUS_COLORS:
            status_btn.setStyleSheet(f"background-color: {self.STATUS_COLORS[status]}")
        else:
            status_btn.setStyleSheet("")

    def retrieve_instance_status(self, instance_id):
        ec2_client = self.session.client("ec2", region_name=self.instances[instance_id]["region"])
        response = ec2_client.describe_instances(InstanceIds=[instance_id])
        instance = response["Reservations"][0]["Instances"][0]
        status = instance["State"]["Name"]
        return status, instance["PublicIpAddress"] if status == "running" else "--"

    def describe_instance_status(self):
        sender: QPushButton = cast(QPushButton, self.sender())
        if sender:
            row = self.instances_table.indexAt(sender.pos()).row()
            instance_id = self.instances_table.item(row, 0).text()
            status, ip = self.retrieve_instance_status(instance_id)
            self._display_status(sender, status)
            if status == "running":
                self.instances_table.item(row, 3).setText(ip)
            else:
                self.instances_table.item(row, 3).setText("--")
            self.waiting_sth = False

    def start_instance(self):
        sender = self.sender()
        if sender:
            row = self.instances_table.indexAt(sender.pos()).row()
            instance_id = self.instances_table.item(row, 0).text()
            ec2_client = self.session.client("ec2", region_name=self.instances[instance_id]["region"])
            start_res = ec2_client.start_instances(InstanceIds=[instance_id])
            status_btn = cast(QPushButton, self.instances_table.cellWidget(row, 2))
            status = start_res["StartingInstances"][0]["CurrentState"]["Name"]
            self.instances_status[instance_id] = status
            self._display_status(status_btn, status)
            if status != "running":
                self.waiting_sth = True
                waiter = ec2_client.get_waiter("instance_running")
                waiter.wait(InstanceIds=[instance_id])
                response = ec2_client.describe_instances(InstanceIds=[instance_id])
                instance = response["Reservations"][0]["Instances"][0]
                self.instances_status[instance_id] = instance["State"]["Name"]
                self._display_status(status_btn, instance["State"]["Name"])
                self.instances_table.item(row, 3).setText(instance["PublicIpAddress"])
                print(f"Public IP address: {instance['PublicIpAddress']}")
                self.waiting_sth = False
            self.adjust_main_widget_width()

    def stop_instance(self):
        sender = self.sender()
        if sender:
            row = self.instances_table.indexAt(sender.pos()).row()
            instance_id = self.instances_table.item(row, 0).text()
            ec2_client = self.session.client("ec2", region_name=self.instances[instance_id]["region"])
            stop_res = ec2_client.stop_instances(InstanceIds=[instance_id])
            status = stop_res["StoppingInstances"][0]["CurrentState"]["Name"]
            status_btn = cast(QPushButton, self.instances_table.cellWidget(row, 2))
            self.instances_status[instance_id] = status
            self._display_status(status_btn, status)
            if status != "stopped":
                self.waiting_sth = True
                waiter = ec2_client.get_waiter("instance_stopped")
                waiter.wait(InstanceIds=[instance_id])
                response = ec2_client.describe_instances(InstanceIds=[instance_id])
                instance = response["Reservations"][0]["Instances"][0]
                status = instance["State"]["Name"]
                self._display_status(status_btn, status)
                self.instances_status[instance_id] = status
                self.instances_table.item(row, 3).setText("--")
                self.waiting_sth = False
            self.adjust_main_widget_width()

    def edit_security_group(self):
        sender = self.sender()
        if sender:
            row = self.instances_table.indexAt(sender.pos()).row()
            sg_id = self.instances_table.item(row, 6).text()
            self.security_group_editor = SecurityGroupEditor(sg_id, self.session)
            self.security_group_editor.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)
            self.security_group_editor.show()

    def closeEvent(self, event):
        if self.waiting_sth or any(status in {"pending", "stopping"} for status in self.instances_status.values()):
            event.ignore()
            return
        if any(status == "running" for status in self.instances_status.values()):
            res = QMessageBox.question(
                self,
                "Warning",
                "Some instances are still running. Do you want to close the application?",
                QMessageBox.Yes | QMessageBox.No,
            )
            if res == QMessageBox.No:
                event.ignore()
                return
        event.accept()

    def load_all_available_instances(self):
        all_instances_by_region = self.retrieve_instances_all_regions()
        with open(Path.home().joinpath(".aws_ec2.yaml"), "w") as f:
            yaml = YAML(typ="safe")
            yaml.dump(
                {
                    "authorization_profile": self.authorization_profile,
                    "load_status_at_start": self.load_status_at_start,
                    "instances": all_instances_by_region,
                },
                f,
            )
        self.instances = {}
        for region, instance_ids in all_instances_by_region.items():
            self.instances.update(
                {
                    instance_id: {"id": instance_id, "region": region, "security_group": ""}
                    for instance_id in instance_ids
                }
            )
            if self.load_status_at_start:
                ec2_client = self.session.client("ec2", region_name=region)
                response = ec2_client.describe_instances(InstanceIds=instance_ids)
                for reservation in response["Reservations"]:
                    for instance in reservation.get("Instances", []):
                        self.instances_status[instance["InstanceId"]] = instance["State"]["Name"]
                        self.instances[instance["InstanceId"]]["security_group"] = instance["SecurityGroups"][0][
                            "GroupId"
                        ]
            else:
                self.instances_status.update(
                    {instance_id: "Unknown" for instance_id in instance_ids if instance_id not in self.instances_status}
                )

        for instance_id in set(self.instances_status.keys()) - set(self.instances.keys()):
            del self.instances_status[instance_id]

        QMessageBox.information(self, "Information", "All available instances have been reloaded.")

    def retrieve_instances_all_regions(self):
        ec2_client = self.session.client("ec2")
        regions = [region["RegionName"] for region in ec2_client.describe_regions()["Regions"]]
        all_instances = {}
        for region in regions:
            ec2_client = self.session.client("ec2", region_name=region)
            response = ec2_client.describe_instances()
            for reservation in response["Reservations"]:
                all_instances.setdefault(region, []).extend(
                    [instance["InstanceId"] for instance in reservation["Instances"]]
                )
        return all_instances
