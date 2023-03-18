# 监视“学生考试安排”

```shell
> just update
INFO:root:Got the URL of “12.1更新”: https://jxzx.bit.edu.cn/docs/2022-12/64a5e551792842e2a305a62e56ee8bde.xlsx .
（测试）我们班相关的“学生考试安排”如下。（12.1更新）

- **复变函数与数理方程**

  2022-12-05 18:30-20:30（星期一）

> 考试说明查询地址：https://lexue.bit.edu.cn/course/view.php?id=11614

……
详情见[教学中心通知](https://jxzx.bit.edu.cn/tzgg/9791433d77d044b6bed2e07c50b02319.htm)。
INFO:root:The message was saved to D:\DevelopProjects\Archive\2036\watch\output\message.txt.
```

```shell
# ↓ 查看更多信息
> python -m watch_exams --help
> just --list
```

## ⚙️设置（`config/`）

- `watches.csv`

  必需有。

  关心的同学的姓名、学号，每行一个。`#`打头的行算注释。

  示例如下。

  ```csv
  姓名,学号
  李白,1107010228
  # 杜甫很遗憾成为了注释
  苏轼,1110370108
  ```

- `ding_secrets.txt`

  只有用`--ding`时才需要。

  钉钉自定义 webhook 机器人的信息。

  - 第一行

    访问密钥：`https://oapi.dingtalk.com/robot/send?access_token=`之后的东西。

  - 第二行

    加的签：机器人设置 → 安全设置 → 加签，`SEC`打头。
  
  示例如下。

  ```
  08cdd541575a6b15b68faf70e1b2c5160a744c7f64771df301afe5c1ba85e58c
  SEC2deaf1250fc694382d1294a4e74974d9f3b9868e6d25f6a775e6a33cbf931510
  # 这儿也可有注释
  ```

## 📋输出（`output/`）

- `message.txt`

  上一次的结果，markdown 格式。

- `message-old.txt`
  
  更改`message.txt`时进行的备份。

## 🛠️开发

```shell
$ poetry install
$ poetry run watch_exams --help
```

运行并不一定需要 [Poetry](https://python-poetry.org/) 或 [just](https://just.systems/)。
