import vlc
vlcInstance = vlc.Instance()
player = vlcInstance.media_player_new('videoplayback.mp4')
player.set_mrl("rtsp://@224.0.0.100")
player.play()
