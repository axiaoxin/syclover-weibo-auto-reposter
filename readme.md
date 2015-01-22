自动转发@自己的微博
===================


**使用方法**

在crontab中配置好微博帐号信息的环境变量设置每5分钟检测转发一次就可以辣.

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

- .atme_since_id 保存在原创或转发微博中@自己的最近一条微博ID，避免重复转发
- .comment_since_id 保存在评论中@到自己的最近一条微博ID，避免重复转发（如果别人回复了你的评论也会产生@自己的评论会被转发，如：回复@阿小信大人:你是个好人）
- .syclover-auto-weibo.log 日志文件
