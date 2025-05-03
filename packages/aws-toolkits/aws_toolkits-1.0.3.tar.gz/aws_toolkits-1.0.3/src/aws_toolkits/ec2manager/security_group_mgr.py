# -*- coding: utf-8 -*-
# @Time    : 2025/3/18 16:16
# @Author  : YQ Tsui
# @File    : security_group_mgr.py
# @Purpose : manage security group inbound rules

import re
import requests
from PySide6.QtWidgets import (
    QMessageBox,
    QPushButton,
    QSizePolicy,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)


def get_external_ip():
    text = requests.get("https://myip.ipip.net", timeout=5).text
    obj = re.search(r"[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+", text)
    return obj.group() + "/32"


class InBoundRuleTable(QTableWidget):

    def __init__(self, sg_info, parent=None):
        super().__init__(parent)
        self.sg_info = sg_info
        self.sg_info_mapping = None
        self.init_ui()

    def init_ui(self):
        self.setColumnCount(4)
        self.setFixedWidth(390)
        self.verticalHeader().setVisible(False)
        self.setHorizontalHeaderLabels(["Protocol", "Port Range", "Source", "Action"])
        self.setColumnWidth(0, 90)
        self.setColumnWidth(1, 90)
        self.setColumnWidth(2, 110)
        self.setColumnWidth(3, 100)
        ip_permissions = self.sg_info.get("IpPermissions", [])
        self.sg_info_mapping = {(rule["IpProtocol"], rule["FromPort"], rule["ToPort"]): rule for rule in ip_permissions}
        self.setRowCount(0)
        for row, rule in enumerate(ip_permissions):
            ip_range = rule.get("IpRanges", [])
            cidr_ips = [ip_range["CidrIp"] for ip_range in ip_range if "CidrIp" in ip_range]
            if not cidr_ips:
                continue
            protocol = rule.get("IpProtocol", "-")
            from_port = str(rule.get("FromPort", "All"))
            to_port = str(rule.get("ToPort", "All"))
            port_range = f"{from_port}-{to_port}" if from_port != to_port else from_port
            for cidr_ip in cidr_ips:
                row = self.rowCount()
                self.insertRow(row)
                self.setItem(row, 0, QTableWidgetItem(protocol))
                self.setItem(row, 1, QTableWidgetItem(port_range))
                self.setItem(row, 2, QTableWidgetItem(cidr_ip))
                btn = QPushButton("Set to My IP")
                btn.setFixedWidth(100)
                btn.clicked.connect(self.set_to_my_ip)
                self.setCellWidget(row, 3, btn)

    def update_sg_info(self, sg_info):
        self.sg_info = sg_info
        self.clear()
        self.init_ui()

    def set_to_my_ip(self):
        sender = self.sender()
        if sender:
            row = self.indexAt(sender.pos()).row()
            self.item(row, 2).setText(get_external_ip())

    def collect_data(self):
        to_revoke = []
        to_authorize = []

        for row in range(self.rowCount()):
            protocol = self.item(row, 0).text()
            port_range = self.item(row, 1).text()
            if "-" in port_range:
                from_port, to_port = map(int, port_range.split("-"))
            else:
                from_port = to_port = int(port_range)
            source = self.item(row, 2).text()
            old_rule = self.sg_info_mapping.get((protocol, from_port, to_port))
            if len(old_rule["IpRanges"]) != 1 or old_rule["IpRanges"][0]["CidrIp"] != source:
                to_revoke.append(old_rule)
                to_authorize.append(
                    {
                        "IpProtocol": protocol,
                        "FromPort": from_port,
                        "ToPort": to_port,
                        "IpRanges": [
                            {
                                "CidrIp": source,
                            }
                        ],
                    }
                )

        return to_revoke, to_authorize


class SecurityGroupEditor(QWidget):

    def __init__(self, security_group_id: str, ec2_session, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Security Group Editor")
        self.id = security_group_id
        self.session = ec2_session
        self.sg_info = self.retrieve_security_group_infos(security_group_id)
        self.init_ui()

    def retrieve_security_group_infos(self, sg_id: str):
        ec2_client = self.session.client("ec2")
        sg_data = ec2_client.describe_security_groups(GroupIds=[sg_id])
        return sg_data["SecurityGroups"][0]

    def init_ui(self):
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.inbound_table = InBoundRuleTable(self.sg_info, parent=self)
        self.update_btn = QPushButton("Update")
        self.update_btn.clicked.connect(self.update_inbound_rules)

        vbox = QVBoxLayout()
        vbox.addWidget(self.inbound_table)
        vbox.addWidget(self.update_btn)
        self.setLayout(vbox)

    def update_inbound_rules(self):
        to_revoke, to_authorize = self.inbound_table.collect_data()
        ec2_client = self.session.client("ec2")
        res_revoke = ec2_client.revoke_security_group_ingress(GroupId=self.id, IpPermissions=to_revoke)
        if res_revoke.get("Return", False):
            res_auth = ec2_client.authorize_security_group_ingress(GroupId=self.id, IpPermissions=to_authorize)
            if res_auth.get("Return", False):
                self.sg_info = self.retrieve_security_group_infos(self.id)
                self.inbound_table.update_sg_info(self.sg_info)
                QMessageBox.information(self, "Information", "Inbound rules have been updated.")
            else:
                QMessageBox.warning(self, "Warning", "Failed to update inbound rules." + str(res_auth))
        else:
            QMessageBox.warning(self, "Warning", "Failed to update inbound rules." + str(res_revoke))
