自动转发@自己的微博
===================


使用方法：

1，配置微博帐号信息：

    export PASSWORD=W3!b0_Mim4
    export ACCOUNT=weibo_zh4ngha0
    export REDIRECT_URI=your_app_redirect_uri
    export APP_SECRET=s3cr3t
    export APP_KEY=iamappkey

2, 设置crontab：

    crontab -e

添加每五分钟检查一次是否有人@：

    */5 * * * * python /PATH/TO/syclover_auto_weibo.py
