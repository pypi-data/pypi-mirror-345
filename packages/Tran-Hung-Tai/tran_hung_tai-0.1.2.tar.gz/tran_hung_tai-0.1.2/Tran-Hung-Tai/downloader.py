import requests
from tqdm import tqdm

RAPIDAPI_KEY = "13113fd5abmsh5bc1fd3afd85727p18eb38jsncef680087072"  # Gắn cứng ở đây

def download_video(tiktok_url, save_path="video.mp4"):
    url = "https://tiktok-downloader-download-tiktok-videos-without-watermark.p.rapidapi.com/index"
    querystring = {"url": tiktok_url}
    headers = {
        "x-rapidapi-key": RAPIDAPI_KEY,
        "x-rapidapi-host": "tiktok-downloader-download-tiktok-videos-without-watermark.p.rapidapi.com"
    }

    print("🔍 Đang lấy link video...")
    response = requests.get(url, headers=headers, params=querystring)
    result = response.json()

    if "video" not in result or not result["video"]:
        raise Exception("❌ Không tìm thấy URL video trong dữ liệu API")

    video_url = result["video"][0]
    print("🎥 Đang tải video...")

    with requests.get(video_url, stream=True) as r:
        r.raise_for_status()
        total = int(r.headers.get('content-length', 0))
        with open(save_path, 'wb') as f, tqdm(
            desc=save_path,
            total=total,
            unit='iB',
            unit_scale=True,
            unit_divisor=1024,
            ncols=80
        ) as bar:
            for chunk in r.iter_content(chunk_size=65536):  # 64KB
                f.write(chunk)
                bar.update(len(chunk))

    print("✅ Tải xong:", save_path)
