import datetime
import difflib
import json
import re
import time

import bs4
import lxml
import zbToolLib as f


class MccnVersion:
    versions = {"status": "loading"}
    isLoading = False


    def getFromListFile(self, url):
        """
        解析list文件形式的版本信息Api
        :param url: Api地址
        :return: 列表形式的数据，每个元素为一行数据的字典
        """
        text = f.getUrl(url, f.REQUEST_HEADER).text
        text = text.split("\n")
        text = [json.loads(("{" + i.rstrip(",") + "}")) for i in text if i]
        return text

    def getFromJsonFile(self, url):
        """
        解析json文件形式的版本信息Api
        :param url: Api地址
        :return: 字典形式的数据
        """
        return json.loads(f.getUrl(url, f.REQUEST_HEADER).text)

    def _getG79Version(self, data, name: str = "", patch_version=""):
        import base64
        if name != "官服":
            return {"name": name, "version": data["version"], "patch_version": patch_version, "minimum_version": data["min_ver"], "url": data["url"], "update_notice": base64.b64decode(data["text"]).decode("utf-8")}
        else:
            return {"name": name, "version": data["version"], "patch_version": patch_version, "website_version": None, "minimum_version": data["min_ver"], "url": data["url"], "website_url": None, "update_notice": base64.b64decode(data["text"]).decode("utf-8")}

    def _getG79PatchVersion(self, data: dict, version):
        l = []
        for i in data:
            if i.split(".")[:2] == version.split(".")[:2]:
                l.append(i)
        return l[-1]

    def _getG79DevLogUrl(self, version_type: str):
        v = ".".join(version_type.rstrip("beta").rstrip("stable").split(".")[0:2])
        if version_type.endswith("beta") and not "404" in f.getUrl(f"https://mc.163.com/dev/mcmanual/mc-dev/mcdocs/1-ModAPI-beta/更新信息/{v}.html", f.REQUEST_HEADER).text:
            return f"https://mc.163.com/dev/mcmanual/mc-dev/mcdocs/1-ModAPI-beta/更新信息/{v}.html"
        else:
            return f"https://mc.163.com/dev/mcmanual/mc-dev/mcdocs/1-ModAPI/更新信息/{v}.html"

    def _getG79WebsiteDownloadUrl(self):
        try:
            res = f.getUrl(r"https://adl.netease.com/d/g/mc/c/gwnew?type=android", f.REQUEST_HEADER)
            res = lxml.etree.HTML(res.text)
            name = res.xpath("/html/body/script[2]/text()")[0]
            pattern = r'var android_link = android_type \?\s*"(https?://[^"]+)"\s*:\s*"(https?://[^"]+)"\s*;'
            match = re.search(pattern, name)
            return match.group(1).split("?")[0]
        except:
            return None
    def _getG79IOSIconUrl(self):

        try:
            res = f.getUrl("https://apps.apple.com/cn/app/%E6%88%91%E7%9A%84%E4%B8%96%E7%95%8C-%E7%A7%BB%E5%8A%A8%E7%89%88/id1243986797", f.REQUEST_HEADER)
            res = lxml.etree.HTML(res.text)
            return "/".join(res.xpath("/html/head/meta[15]/@content")[0].split("/")[:-1])+"/1024x1024bb.png"
        except:
            return None

    def _getG79DevIOSIconUrl(self):
        try:
            res = f.getUrl("https://testflight.apple.com/join/mOxZm1dD", f.REQUEST_HEADER)
            res = lxml.etree.HTML(res.text)
            return "/".join(res.xpath("/html/head/meta[14]/@content")[0].split("/")[:-1])+"/1024x1024bb.png"
        except:
            return None

    def getG79Versions(self):
        """
        获取我的世界中国版手游最新版本数据
        :return: 字典形式的数据
        """
        website_url = self._getG79WebsiteDownloadUrl()
        result = {"name": "手游版启动器", "release": {"name": "正式版"}, "preview": {}, "developer": {"name": "开发者测试版", "android": {"name": "Android", "latest": {"name": "最新版本"}, "old": {"name": "上一版本"}}, "ios": {"name": "iOS", "latest": {"name": "最新版本"}}}}
        urls = {
            "download-version": "https://mc-launcher.webapp.163.com/users/get/download-version",
            "pe": "https://mc-launcher.webapp.163.com/users/get/download/pe",
            "pe_old": "https://mc-launcher.webapp.163.com/users/get/download/pe_old",
            "g79_packlist_2": "https://g79.update.netease.com/pack_list/production/g79_packlist_2",
            "g79_rn_patchlist": "https://g79.update.netease.com/patch_list/production/g79_rn_patchlist",
        }
        names = {"baidu": ["百度渠道服", "baidu"],
                 "douyin": ["抖音渠道服", "douyin"],
                 "lenovo_open": ["联想渠道服", "lenovo"],
                 "coolpad_sdk": ["酷派渠道服", "coolpad"],
                 "nearme_vivo": ["vivo渠道服", "vivo"],
                 "uc_platform": ["UC渠道服", "uc"],
                 "kuaishou_new": ["快手渠道服", "kuaishou"],
                 "4399com": ["4399渠道服", "4399"],
                 "honor_sdk": ["荣耀渠道服", "honor"],
                 "huawei": ["华为渠道服", "huawei"],
                 "233leyuan": ["233乐园渠道服", "233leyuan"],
                 "360_assistant": ["360渠道服", "360"],
                 "myapp": ["应用宝渠道服", "yingyongbao"],
                 "nubia": ["努比亚渠道服", "nubia"],
                 "xiaomi_app": ["小米渠道服", "xiaomi"],
                 "oppo": ["OPPO渠道服", "oppo"],
                 "bilibili_sdk": ["BiliBili渠道服", "bilibili"],
                 }

        data1 = self.getFromJsonFile(urls["g79_packlist_2"])
        data2 = self.getFromJsonFile(urls["g79_rn_patchlist"])
        data3 = self.getFromJsonFile(urls["download-version"])["data"]
        data4 = self.getFromJsonFile(urls["pe"])["data"]
        data5 = self.getFromJsonFile(urls["pe_old"])["data"]

        result["release"]["official"] = self._getG79Version(data1["netease"], "官服", self._getG79PatchVersion(data2["android"], data1["netease"]["version"]))
        result["release"]["official"]["website_version"] = re.search(r'(\d+\.\d+\.\d+\.\d+)', website_url).group(1) if website_url else None
        result["release"]["official"]["website_url"] = website_url
        result["release"]["ios"] = self._getG79Version(data1["app_store"], "iOS服", self._getG79PatchVersion(data2["ios"], data1["app_store"]["version"]))
        result["release"]["ios"]["icon"]=self._getG79IOSIconUrl()
        result["release"]["taptap"] = self._getG79Version(data1["netease.taptap2_cps_dev"], "TapTap官服", self._getG79PatchVersion(data2["android"], data1["netease.taptap2_cps_dev"]["version"]))
        result["release"]["hykb"] = self._getG79Version(data1["netease.hykb_cps_dev"], "好游快爆官服", self._getG79PatchVersion(data2["android"], data1["netease.hykb_cps_dev"]["version"]))
        for i in data1.keys():
            if i not in ["netease", "ios", "netease.taptap2_cps_dev", "netease.hykb_cps_dev", "app_store"]:
                result["release"][names[i][1]] = self._getG79Version(data1[i], names[i][0], self._getG79PatchVersion(data2["android"], data1[i]["version"]))
        if data1["netease"]["text"]:
            result["preview"] = self._getG79Version(data1["netease"], "抢先体验版", self._getG79PatchVersion(data2["android"], data1["netease"]["version"]))
        else:
            result["preview"] = None

        result["developer"]["android"]["latest"]["version"] = data4["url"].replace("https://g79.gdl.netease.com/dev_launcher_", "").replace(".apk", "")
        result["developer"]["android"]["latest"]["version_type"] = data3["pe"]
        result["developer"]["android"]["latest"]["url"] = data4["url"]
        result["developer"]["android"]["latest"]["log_url"] = self._getG79DevLogUrl(data3["pe"])
        result["developer"]["android"]["old"]["version"] = data5["url"].replace("https://g79.gdl.netease.com/dev_launcher_", "").replace(".apk", "")
        result["developer"]["android"]["old"]["version_type"] = data3["pe_old"]
        result["developer"]["android"]["old"]["url"] = data5["url"]
        result["developer"]["android"]["old"]["log_url"] = self._getG79DevLogUrl(data3["pe_old"])
        result["developer"]["ios"]["latest"]["icon"] = self._getG79DevIOSIconUrl()
        return result

    def _getX19Version(self, data, name: str = "", debug: bool = False):
        v = list(data[-1].keys())[0]
        version = None
        log = ""
        if not debug:
            url = f"https://x19.update.netease.com/MCUpdate_{".".join(v.split(".")[:3])}.txt"
            try:
                log = f.getUrl(url, f.REQUEST_HEADER)
                if log.status_code != 200:
                    raise Exception
                log.encoding = "GB2312"
                log = log.text
            except:
                pass
        else:
            for i in data[::-1]:
                if "exe" in list(i.values())[0]["url"]:
                    version = list(i.keys())[0]
                    break
        return {"name": name, "version": version, "patch_version": v, "log": log, "url": None, "patch_url": list(data[-1].values())[0]["url"]}

    def _getX19WebsiteDownloadUrl(self):
        try:
            res = f.getUrl(r"https://adl.netease.com/d/g/mc/c/pc?type=pc", f.REQUEST_HEADER)
            res = lxml.etree.HTML(res.text)
            name = res.xpath("/html/body/script[2]/text()")[0]
            pattern = r'var pc_link = "(https?://[^"]+)"\s*;'
            match = re.search(pattern, name)
            return match.group(1).split("?")[0]
        except:
            return None

    def getX19Versions(self):
        """
        获取我的世界中国版端游最新版本
        :return: 字典形式的数据
        """
        website_url = self._getX19WebsiteDownloadUrl()
        result = {"name": "端游版启动器", "release": {"name": "正式版"}, "debug": {"name": "调试版"}}
        urls = {"x19_java_patchlist": "https://x19.update.netease.com/pl/x19_java_patchlist",
                "x19_patch_list_debug": "https://x19.update.netease.com/pl/x19_patch_list_debug",
                "A50SdkCn_x19_java_patchlist": "https://x19.update.netease.com/pl/A50SdkCn_x19_java_patchlist",
                "A50SdkCn_x19_patch_list_debug": "https://x19.update.netease.com/pl/A50SdkCn_x19_patch_list_debug",
                "PC4399_x19_java_patchlist": "https://x19.update.netease.com/pl/PC4399_x19_java_patchlist",
                "PC4399_x19_patch_list_debug": "https://x19.update.netease.com/pl/PC4399_x19_patch_list_debug",
                }
        result["release"]["official"] = self._getX19Version(self.getFromListFile(urls["x19_java_patchlist"]), "官服")
        result["release"]["official"]["url"] = website_url
        result["release"]["official"]["version"] = re.search(r'(\d+\.\d+\.\d+\.\d+)', website_url).group(1) if website_url else None
        result["debug"]["official"] = self._getX19Version(self.getFromListFile(urls["x19_patch_list_debug"]), "官服", True)
        result["release"]["fever"] = self._getX19Version(self.getFromListFile(urls["A50SdkCn_x19_java_patchlist"]), "发烧平台官服")
        result["release"]["fever"]["version"] = re.search(r'(\d+\.\d+\.\d+\.\d+)', website_url).group(1) if website_url else None
        result["debug"]["fever"] = self._getX19Version(self.getFromListFile(urls["A50SdkCn_x19_patch_list_debug"]), "发烧平台官服", True)
        result["release"]["4399"] = self._getX19Version(self.getFromListFile(urls["PC4399_x19_java_patchlist"]), "4399渠道服")
        result["release"]["4399"]["url"] = "https://dl.img4399.com/download/4399wdsj.exe"
        result["release"]["4399"]["version"] = re.search(r'(\d+\.\d+\.\d+\.\d+)', website_url).group(1)
        result["debug"]["4399"] = self._getX19Version(self.getFromListFile(urls["PC4399_x19_patch_list_debug"]), "4399渠道服", True)
        return result

    def _getMCSVersion(self, data, name: str = ""):
        v = list(data[-1].keys())[0]
        url = f"https://x19.update.netease.com/game_notice/MCStudio_{".".join(v.split(".")[:3])}.txt"
        try:
            log = f.getUrl(url, f.REQUEST_HEADER)
            if log.status_code != 200:
                raise Exception
            log.encoding = "utf-8"
            log = log.text
        except:
            log = ""
        log_url, date = self._getMCSUrl(v)
        website_url = self._getMCSWebsiteDownloadUrl()
        return {"name": name, "version": re.search(r'(\d+\.\d+\.\d+\.\d+)', website_url).group(1) if website_url else None, "patch_version": v, "patch_date": date, "log": log, "url": website_url, "patch_url": list(data[-1].values())[0]["url"], "log_url": log_url}

    def _getMCSUrl(self, version: str):
        v = ".".join(version.split(".")[:3])
        res = f.getUrl(r"https://mc.163.com/dev/mcmanual/mc-dev/mcguide/10-新内容/1-开发工作台/946-1.1.22.html", f.REQUEST_HEADER)
        res.encoding = "utf-8"
        soup = bs4.BeautifulSoup(res.text, "lxml")
        for i in soup.find_all(name="a"):
            if v in i.text:
                try:
                    return "https://mc.163.com" + i["href"].replace("?catalog=1", ""), i.text.replace("版本", "").replace(v, "").strip()
                except:
                    return None, None

    def _getMCSWebsiteDownloadUrl(self):
        try:
            res = f.getUrl(r"https://adl.netease.com/d/g/mc/c/dev", f.REQUEST_HEADER)
            res = lxml.etree.HTML(res.text)
            name = res.xpath("/html/body/script[2]/text()")[0]
            pattern = r'var pc_link = "(https?://[^"]+)"\s*;'
            match = re.search(pattern, name)
            return match.group(1).split("?")[0]
        except:
            return None

    def getMCSVersions(self):
        """
        获取MC Studio最新版本
        :return: 字典形式的数据
        """
        urls = {"mcstudio_release_patchlist": "https://x19.update.netease.com/pl/mcstudio_release_patchlist"}
        result = self._getMCSVersion(self.getFromListFile(urls["mcstudio_release_patchlist"]), "MC Studio")

        return result

    def get(self):
        """
        获取我的世界中国版最新版本
        :return: 字典形式的数据
        """
        result = {"status": "success", "time": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "timestamp": int(time.time()), "g79": self.getG79Versions(), "x19": self.getX19Versions(), "mcstudio": self.getMCSVersions()}
        return result
