@commands.command()
async def convert(self, ctx, url, conversion_type="mp4"):
    try:
        yt = YouTube(url)

        if yt.age_restricted:
            await ctx.send("This video is age-restricted and cannot be converted.")
            return

        stream = yt.streams.filter(progressive=True, file_extension='mp4').order_by('resolution').desc().first()

        if not stream:
            await ctx.send("Could not find a suitable video stream for download.")
            return

        duration = yt.length

        if duration > max_video_duration:
            await ctx.send("Video exceeds the maximum time limit of 10 minutes.")
            return

        await ctx.send("Converting the video, please wait...")
        video_name = yt.title
        video_path = f'/mnt/converter/{video_name}-{ctx.author.id}.{conversion_type}'

        if conversion_type == "mp4":
            stream.download(filename=video_path)
        elif conversion_type == "mp3":
            os.system(f'ffmpeg -i "{video_path}" "{video_path}.mp3"')
            video_path = f'{video_path}.mp3'

        if os.path.getsize(video_path) > max_file_size_bytes:
            await ctx.send("The file is too big to be converted. It must be under 25MBs. This is Discord's fault, not mine.")
            os.remove(video_path)
            return

        await ctx.send(f'{ctx.author.mention}, your video conversion is complete. Here is the converted video:', file=discord.File(video_path))
        await ctx.trigger_typing()
        os.remove(video_path)  # Clean up the converted file
    except Exception as e:
        error_message = str(e)
        await ctx.send(f"An error occurred during video conversion. Please check the URL and try again.\nError details: {error_message}")
