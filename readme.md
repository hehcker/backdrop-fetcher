# backdrop fetcher

a simple client for grabbing wallpapers list from google server used in [google wallpaper picker](https://play.google.com/store/apps/details?id=com.google.android.apps.wallpaper) (aka wallpaper & style)

## setup
1. **install python dependencies**
    ```
    $ pip install requests protobuf
    ```
2. **install protobuf compiler**
 
    **windows**:
    - download protoc-*version*-win**.zip from [official repository](https://github.com/protocolbuffers/protobuf/releases)
    - extract bin\protoc.exe somewhere
    
    **linux**:
    - install the `protoc` package with your favorite package manager

    ### !!make sure that version of `protoc` is the same as the version of the `protobuf` python library!!
    ```
    $ protoc --version
    libprotoc 32.1
    ```
    ```
    $ pip show protobuf
    Name: protobuf
    Version: 6.32.1 <- ignore 6.
    Summary:
    ```

3. **compile .proto**
    ```
    $ protoc -I=. --python_out=. imax_wallpaper.proto
    ```
    --python_out should be directory with backdrop_fetcher.py 

## usage
run backdrop fetcher:

```
$ python backdrop_fetcher.py
```

you will get a json output:
```
{
  "collections": [
    {
      "collection_name": "Community Lens",
      "collection_id": "community_lens",
      "wallpapers": [
        {
          "asset_id": 0,
          "image_url": "https://lh5.googleusercontent.com/proxy/verygoodimage=s0",
          "action_url": "",
          "attributions": [
            "name",
            "description"
          ],
          "type": 0
        }
        ...
      ]
    }
  ]
} 
```

check backdrop_fetcher.py for more info

## todo 
- integrate backdrop fetcher into aosp [wallpaper picker](https://android.googlesource.com/platform/packages/apps/WallpaperPicker2)