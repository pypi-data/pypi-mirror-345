import re
from typing import List, Iterator


class Txt2Json:
    def __init__(self, path, *, encoding='utf-8'):
        """
        Web of Science 下载的纯文本转为字典格式
        :param path: 纯文本的地址路径
        :param encoding: 文本编码
        """
        self.block = re.compile(r"(?=\n[A-Z0-9]{2})")
        self.encoding = encoding
        self.data = self._read_file(path)

    def _read_file(self, path) -> List[str]:
        """读取并处理文件，跳过前两行，返回非空数据块列表"""
        with open(path, 'r', encoding=self.encoding) as fp:
            fn = fp.readline().strip()
            vr = fp.readline().strip()
            content = fp.read().strip().split("\n\n")
            text = []

            if not fn.encode('utf8').startswith(b'\xef\xbb\xbf') and fn:
                text.append(fn)

            if vr and not vr.startswith("VR"):
                text.append(vr)

            if not content:
                return text

            if content[-1] == "EF":
                content.pop()

            text.extend(content)
            return text

    def __getitem__(self, i: int) -> dict:
        """生成第i快"""
        data = self.data[i]
        return self._parse_(self._cut(data))

    def _cut(self, data) -> List[str]:
        """每个数据块分割后的字段列表"""
        fields = self.block.split(data)
        return [field.strip() for field in fields if field.strip()]

    def __iter__(self) -> Iterator[List[str]]:
        """迭代生成每个数据块分割后的字段列表"""
        for data in self.data:
            yield self._cut(data)

    def __len__(self) -> int:
        """返回数据块数量"""
        return len(self.data)

    @staticmethod
    def _parse_(lines) -> dict:
        value_dict = {}
        for line in lines:
            line = line.strip()
            if not line:
                continue
            key, value = line[:2], line[3:]
            multiple = [v.strip() for v in value.split("\n") if v.strip()]
            value_dict[key] = value if len(multiple) <= 1 else multiple
        return value_dict

    def json(self) -> List[dict]:
        """将数据转换为结构化JSON格式"""
        result = []
        for lines in self.__iter__():
            value = self._parse_(lines)
            result.append(value)
        return result

    def df(self):
        try:
            import pandas as pd
        except ImportError:
            raise ImportError("pip install pandas")

        return pd.DataFrame(self.json())


if __name__ == '__main__':
    import os

    dirs = os.path.dirname(os.path.dirname(__file__))
    p = os.path.join(dirs, 'Analytics Web of Science.txt')
    process = Txt2Json(p)
    print(process.json())
