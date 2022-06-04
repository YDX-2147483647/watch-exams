# 监视“学生考试安排”

```shell
> .\env\Scripts\activate # 如果用 Venv
> python main.py --help
```

## 设置（`config/`）

- `watches.txt`

  必需有。

  关心的同学的名字，每行一个。`#`打头的行算注释。

- `ding_secrets.txt`

  只有用`--ding`时才需要。

  钉钉自定义 webhook 机器人的信息。

  - 第一行

    访问密钥：`https://oapi.dingtalk.com/robot/send?access_token=`之后的东西。

  - 第二行

    加的签：机器人设置 → 安全设置 → 加签，`SEC`打头。

## 输出（`output/`）

- `message.txt`

  上一次的结果，markdown 格式。
