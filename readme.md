自动转发@自己的微博
===================

                 ____             _
                / ___| _   _  ___| | _____   _____ _ __
                \___ \| | | |/ __| |/ _ \ \ / / _ \ '__|
                 ___) | |_| | (__| | (_) \ V /  __/ |
                |____/ \__, |\___|_|\___/ \_/ \___|_|
                       |___/

            _         _         __        __   _ _
           / \  _   _| |_ ___   \ \      / /__(_) |__   ___
          / _ \| | | | __/ _ \   \ \ /\ / / _ \ | '_ \ / _ \
         / ___ \ |_| | || (_) |   \ V  V /  __/ | |_) | (_) |
        /_/   \_\__,_|\__\___/     \_/\_/ \___|_|_.__/ \___/




**使用方法**

在`.syclovers`中填写好每行一个的三叶草成员的微博数字ID，再在crontab中配置好微博帐号信息的环境变量设置每5分钟检测转发一次就可以辣.

在原创微博、转发微博、微博评论中@三叶草小组官微同时加上`转一个`被@的微博就会被官微转发。

只会转发`.syclovers`文件中的限定ID@的微博。

安装依赖：

    sudo pip install -Ur requirements.txt

设置crontab：

    crontab -e

添加内容：

    PASSWORD=your_W3!b0_Mim4
    ACCOUNT=your_weibo_zh4ngha0
    REDIRECT_URI=your_app_redirect_uri
    APP_SECRET=your_s3cr3t
    APP_KEY=your_appkey

    */5 * * * * python /PATH/TO/syclover_auto_weibo.py

**文件说明**

- `syclovers` 三叶草成员微博数字ID列表（每行一个数字ID)

  点击微博右上方你的微博名字那个链接或者私信窗口鼠标移动到昵称上，在url中可以看到数字ID。
  如：`http://weibo.com/1739356367/profile?topnav=1&wvr=6`的ID就为`1739356367`）

- `.syclover-auto-weibo.log` 日志文件
