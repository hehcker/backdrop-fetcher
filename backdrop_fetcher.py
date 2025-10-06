import requests, locale, json
import imax_wallpaper_pb2 as backdrop_pb2

BASE_URL = "https://clients3.google.com/cast/chromecast/home/wallpaper"
COLLECTIONS_ENDPOINT = f"{BASE_URL}/collections?rt=b"
IMAGES_IN_COLLECTION_ENDPOINT = f"{BASE_URL}/collection-images?rt=b"

def get_language():
    try:
        lang, encoding = locale.getdefaultlocale()
        return lang.replace('_', '-')
    except ValueError:
        return "en-US"

# backdrop server processes filtering_labels weirdly: 
# some categories are returned when there is ONLY a "staging" label,
# but chromebook categories are returned if there is "desktop" is AMONG the labels.
def get_filtering_labels():
    return [
        # "staging",

        # all lower extracted from baklava's wallpaper picker
        "update1", # by default
        "nexus", # if (packageManager.hasSystemFeature("com.google.android.feature.PIXEL_EXPERIENCE"))
        "pixel_2017", # if (packageManager.hasSystemFeature("com.google.android.feature.PIXEL_2017_EXPERIENCE"))
        "desktop", # if (packageManager.hasSystemFeature("com.google.desktop.gms"))

        # pixel codename adds two categories: geometric_shapes, community_lens
        "cheetah", # Build.PRODUCT

        # probably doesnt affect to returned categories, but it specified by the wallpaper picker
        "Pixel 7", # Build.MODEL
        "cheetah", # Build.DEVICE
        "android-sdk-36", # "android-sdk-" + Build.VERSION.SDK_INT
        "cheetah.android-sdk-36" # BUILD.Device + "android-sdk-" + Build.VERSION.SDK_INT;
    ]

class BackdropClient:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({"Content-Type": "application/x-protobuf", "Accept": "application/x-protobuf"})
        self.language = get_language()
        self.labels = get_filtering_labels()
        print(f"language {self.language}")
        print(f"labels {self.labels}")

    def get_collections(self):
        request_proto = backdrop_pb2.GetCollectionsRequest()
        request_proto.language = self.language
        request_proto.filtering_label.extend(self.labels)
        serialized_request = request_proto.SerializeToString()
        
        try:
            response = self.session.post(COLLECTIONS_ENDPOINT, data=serialized_request)
            response.raise_for_status()
            response_proto = backdrop_pb2.GetCollectionsResponse()
            response_proto.ParseFromString(response.content)
            return response_proto.collections
        except requests.exceptions.RequestException as e:
            print(f"error: {e}")
            return None

    def get_images_in_collection(self, collection_id: str):
        request_proto = backdrop_pb2.GetImagesInCollectionRequest()
        request_proto.collection_id = collection_id
        request_proto.language = self.language
        request_proto.filtering_label.extend(self.labels)
        serialized_request = request_proto.SerializeToString()

        try:
            response = self.session.post(IMAGES_IN_COLLECTION_ENDPOINT, data=serialized_request)
            response.raise_for_status()
            response_proto = backdrop_pb2.GetImagesInCollectionResponse()
            response_proto.ParseFromString(response.content)
            return response_proto.images
        except requests.exceptions.RequestException as e:
            print(f"error on colletion {collection_id}: {e}")
            return None

def main():
    client = BackdropClient()
    all_data = {}

    collections = client.get_collections()
    if not collections:
        return
    
    total_collections = len(collections)
    print(f"total colletions: {total_collections}")
    
    if "collections" not in all_data:
        all_data["collections"] = []
    
    for i, collection in enumerate(collections):
        print(f"\nfetching {i+1}/{total_collections}: '{collection.collection_name}' id: {collection.collection_id}")
        
        images = client.get_images_in_collection(collection.collection_id)
        
        if not images:
            continue
        
        print(f"images: {len(images)}")

        collection_data = {
            "collection_name": collection.collection_name,
            "collection_id": collection.collection_id,
            "wallpapers": []
        }

        for image in images:
            attributions = [attr.text for attr in image.attribution if attr.text]
            
            wallpaper_info = {
                "asset_id": image.asset_id,
                "image_url": image.image_url
                 + "=s0",  # to get full size, without it, the quality will be 512px (preview..)
                "action_url": image.action_url,
                "attributions": attributions,
                "type": image.type,
            }
            collection_data["wallpapers"].append(wallpaper_info)
        
        all_data["collections"].append(collection_data)

    output_filename = "wallpapers.json"
    with open(output_filename, 'w', encoding='utf-8') as f:
        json.dump(all_data, f, indent=2, ensure_ascii=False)
    
if __name__ == "__main__":
    main()