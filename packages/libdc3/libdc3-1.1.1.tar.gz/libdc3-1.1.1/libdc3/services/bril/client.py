import logging
import os
import os.path
import subprocess
from typing import Optional, Union

import paramiko
from bs4 import BeautifulSoup

from .exceptions import BrilcalcError


logging.getLogger("paramiko").setLevel(logging.WARNING)


class Brilcalc:
    SERVER = "lxplus.cern.ch"
    BRILCONDA = "/cvmfs/cms-bril.cern.ch/brilconda"
    BRILCONDA_BIN = f"{BRILCONDA}/bin"
    BRILCONDA_PY27 = f"{BRILCONDA}/lib/python2.7"
    SWAN_KEY_IN_ENV = "SWAN_LIB_DIR"

    def __init__(
        self,
        keytab_usr: Optional[str] = None,
        keytab_pwd: Optional[str] = None,
        brilws_version: str = "3.7.4",
    ):
        self.brilws_version = brilws_version
        self.local_cvmfs = os.path.isdir(self.BRILCONDA)
        self.ssh_client = self.connect_ssh(keytab_usr, keytab_pwd) if self.local_cvmfs is False else None

    def connect_ssh(self, keytab_usr: str, keytab_pwd: str):
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy)  # noqa: S507
        client.connect(self.SERVER, username=keytab_usr, password=keytab_pwd)
        return client

    def execute_ssh(self, brilcmd: list[str]):
        if self.ssh_client is None:
            raise ValueError(f"{self.BRILCONDA} not found and SSH credentials (keytab_usr, keytab_pwd) are None.")

        command = f"""
        export PATH=$HOME/.local/bin:{self.BRILCONDA_BIN}:$PATH \\
        && pip install --user --upgrade brilws=={self.brilws_version} \\
        && {' '.join(brilcmd)}
        """

        _, stdout, stderr = self.ssh_client.exec_command(command)
        stdout_text = stdout.read().decode("utf-8")
        stderr_text = stderr.read().decode("utf-8")
        return_code = stdout.channel.recv_exit_status()

        return return_code, stdout_text, stderr_text

    def execute_locally(self, brilcmd: list[str]):
        # Add brilconda to path
        user_home = os.path.expanduser("~")
        env = os.environ.copy()
        env["PATH"] = f"{user_home}/.local/bin:{self.BRILCONDA_BIN}:{env['PATH']}"

        # This is needed when executing through CERN's SWAN
        if self.SWAN_KEY_IN_ENV in env:
            env["PYTHONHOME"] = self.BRILCONDA
            env["PYTHONPATH"] = self.BRILCONDA_PY27

        # Install brilws
        # Before directly installing we could check if:
        # `python --version` gives 'Python 2.7.12 :: Continuum Analytics, Inc.'
        # `brilcalc --version` gives 'self.brilws_version'
        install_cmd = [f"{self.BRILCONDA_BIN}/pip", "install", "--user", "--upgrade", f"brilws=={self.brilws_version}"]
        subprocess.run(install_cmd, env=env, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)  # noqa: S603

        # Execute brilcalc command
        out = subprocess.run(brilcmd, shell=False, env=env, capture_output=True)  # noqa: S603
        stdout = out.stdout.decode("utf-8")
        stderr = out.stderr.decode("utf-8")

        return out.returncode, stdout, stderr

    @staticmethod
    def __parse_lumi_html(html, byls: bool = False, unit: str = "/ub"):
        soup = BeautifulSoup(html, "html.parser")
        full_table = soup.find("table")
        summary_table = full_table.find_next("table")

        # Parse full table into a list[dict]
        header, *body = full_table.find_all("tr")
        header = [elem.text for elem in header.find_all("th")]
        body = [[elem.text for elem in body_elem.find_all("td")] for body_elem in body]
        detailed = [dict(zip(header, body_elem)) for body_elem in body]
        for elem in detailed:
            run, fill = elem.pop("run:fill").split(":")
            elem["run"] = int(run)
            elem["fill"] = int(fill)
            elem[f"delivered({unit})"] = float(elem[f"delivered({unit})"])
            elem[f"recorded({unit})"] = float(elem[f"recorded({unit})"])

            # columns that only exists if requesting byls output
            if byls:
                ls_number, _ls_number = elem.pop("ls").split(":")
                elem["ls_number"] = int(ls_number)
                elem["_ls_number"] = int(_ls_number)
                elem["E(GeV)"] = int(elem["E(GeV)"])
                elem["avgpu"] = float(elem["avgpu"])

        # Parse the summary table as a dict
        header, body = summary_table.find_all("tr")
        header = [elem.text for elem in header.find_all("th")]
        body = [elem.text for elem in body.find_all("td")]
        summary = dict(zip(header, body))
        summary["nfill"] = int(summary["nfill"])
        summary["nrun"] = int(summary["nrun"])
        summary["nls"] = int(summary["nls"])
        summary["ncms"] = int(summary["ncms"])
        summary[f"totdelivered({unit})"] = float(summary[f"totdelivered({unit})"])
        summary[f"totrecorded({unit})"] = float(summary[f"totrecorded({unit})"])

        return {"detailed": detailed, "summary": summary}

    def lumi(
        self,
        connect: str = "offline",
        fillnum: Optional[int] = None,
        runnumber: Optional[int] = None,
        beamstatus: Optional[str] = None,
        unit: Optional[str] = "/ub",
        amodetag: Optional[str] = None,
        normtag: Optional[str] = None,
        begin: Optional[Union[str, int]] = None,
        end: Optional[Union[str, int]] = None,
        output_style: str = "tab",
        byls: bool = False,
    ):
        cmd = ["brilcalc", "lumi"]
        if connect:
            cmd.extend(["-c", connect])
        if fillnum:
            cmd.extend(["-f", str(fillnum)])
        if runnumber:
            cmd.extend(["-r", str(runnumber)])
        if beamstatus:
            # If executing with ssh, we need to append quotes to the beamstatus
            if self.local_cvmfs is False:
                beamstatus = f'"{beamstatus}"' if " " in beamstatus else beamstatus
            cmd.extend(["-b", beamstatus])
        if unit:
            cmd.extend(["-u", unit])
        if amodetag:
            cmd.extend(["--amodetag", amodetag])
        if normtag:
            cmd.extend(["--normtag", normtag])
        if begin:
            cmd.extend(["--begin", str(begin)])
        if end:
            cmd.extend(["--end", str(end)])
        if byls is True:
            cmd.extend(["--byls"])
        if output_style:
            cmd.extend(["--output-style", output_style])

        if self.local_cvmfs:
            return_code, stdout, stderr = self.execute_locally(cmd)
            stderr = f"[execute_locally] {stderr}"
        else:
            return_code, stdout, stderr = self.execute_ssh(cmd)
            stderr = f"[execute_ssh] {stderr}"

        if return_code != 0:
            message = f"Error running brilcalc lumi on brilws version {self.brilws_version}.\n\n{' '.join(cmd)}\n\nStderr from command:\n\n{stderr}"
            raise BrilcalcError(message)

        return self.__parse_lumi_html(stdout, byls, unit)
