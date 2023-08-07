import xml.etree.ElementTree as ET

def get_namespace(element):
    if "}" in element.tag:
        return element.tag.split("}")[0].strip("{")
    return ''

def calculate_segments(segments):
    current_time = 0
    all_times = []

    for segment in segments:
        repeat = segment.get('r', 0) + 1
        for _ in range(repeat):
            all_times.append(current_time)
            current_time += segment["d"]
    
    return all_times

def check_url_chunk(url, manifest_path):
    tree = ET.parse(manifest_path)
    root = tree.getroot()
    ns = get_namespace(root)

    # Fetch audio and video adaptation sets
    audio_adaptation_sets = root.findall(".//{%s}AdaptationSet[@contentType='audio']" % ns)
    video_adaptation_sets = root.findall(".//{%s}AdaptationSet[@contentType='video']" % ns)

    print("\nSummary:")
    for audio in audio_adaptation_sets:
        print(f"Audio: Codec={audio.get('codecs')}, Bitrate={audio.get('maxBandwidth')} bps")
    for video in video_adaptation_sets:
        print(f"Video: Codec={video.get('codecs')}, Bitrate={video.get('maxBandwidth')} bps")

    # Validate chunk URL against audio and video adaptation sets
    for audio in audio_adaptation_sets:
        segments = audio.findall("{%s}SegmentTemplate/{%s}SegmentTimeline/{%s}S" % (ns, ns, ns))
        if check_url_against_segments(url, segments):
            return "The audio chunk URL is valid!"
    for video in video_adaptation_sets:
        segments = video.findall("{%s}SegmentTemplate/{%s}SegmentTimeline/{%s}S" % (ns, ns, ns))
        if check_url_against_segments(url, segments):
            return "The video chunk URL is valid!"

    return "The chunk URL is not valid!"

def check_url_against_segments(url, segments):
    parsed_segments = [{"d": int(seg.attrib["d"]), "r": int(seg.attrib.get("r", 0))} for seg in segments]
    all_times = calculate_segments(parsed_segments)

    try:
        chunk_number = int(url.split('-')[-1].split('.')[0])
        return chunk_number in all_times
    except ValueError:
        return False

def total_chunks(manifest_path):
    tree = ET.parse(manifest_path)
    root = tree.getroot()
    ns = get_namespace(root)
    
    audio_adaptation_sets = root.findall(".//{%s}AdaptationSet[@contentType='audio']" % ns)
    video_adaptation_sets = root.findall(".//{%s}AdaptationSet[@contentType='video']" % ns)
    
    audio_chunks = []
    for audio in audio_adaptation_sets:
        segments = audio.findall("{%s}SegmentTemplate/{%s}SegmentTimeline/{%s}S" % (ns, ns, ns))
        audio_chunks.extend(calculate_segments([{"d": int(seg.attrib["d"]), "r": int(seg.attrib.get("r", 0))} for seg in segments]))

    video_chunks = []
    for video in video_adaptation_sets:
        segments = video.findall("{%s}SegmentTemplate/{%s}SegmentTimeline/{%s}S" % (ns, ns, ns))
        video_chunks.extend(calculate_segments([{"d": int(seg.attrib["d"]), "r": int(seg.attrib.get("r", 0))} for seg in segments]))

    return f"Total Audio Chunks: {len(audio_chunks)}, Start: {audio_chunks[0] if audio_chunks else 'N/A'}, End: {audio_chunks[-1] if audio_chunks else 'N/A'}\n" + \
           f"Total Video Chunks: {len(video_chunks)}, Start: {video_chunks[0] if video_chunks else 'N/A'}, End: {video_chunks[-1] if video_chunks else 'N/A'}"

def print_chunk_urls(manifest_path):
    tree = ET.parse(manifest_path)
    root = tree.getroot()
    ns = get_namespace(root)

    audio_adaptation_sets = root.findall(".//{%s}AdaptationSet[@contentType='audio']" % ns)
    video_adaptation_sets = root.findall(".//{%s}AdaptationSet[@contentType='video']" % ns)

    html_content = "<html><head><title>Chunk URLs</title></head><body>"

    def print_chunks_for_adaptation_set(adaptation_set, content_type):
        nonlocal html_content
        html_content += f"<h2>{content_type} Chunk URLs:</h2><ul>"
        
        template = adaptation_set.find("{%s}SegmentTemplate" % ns)
        media = template.get("media")
        representation_id = adaptation_set.find("{%s}Representation" % ns).get("id")

        current_time = 0
        segments = adaptation_set.findall("{%s}SegmentTemplate/{%s}SegmentTimeline/{%s}S" % (ns, ns, ns))
        for seg in segments:
            duration = int(seg.attrib["d"])
            repeat = int(seg.attrib.get('r', 0))
            for _ in range(repeat + 1):  # +1 because repeat=0 means one segment
                final_url = media.replace("$RepresentationID$", representation_id).replace("$Time$", str(current_time))
                html_content += f"<li>{final_url}</li>"
                current_time += duration

        html_content += "</ul>"

    for audio in audio_adaptation_sets:
        print_chunks_for_adaptation_set(audio, "Audio")

    for video in video_adaptation_sets:
        print_chunks_for_adaptation_set(video, "Video")

    html_content += "</body></html>"

    with open("chunk_urls.html", "w") as html_file:
        html_file.write(html_content)

if __name__ == "__main__":
    while True:
        print("\nMenu:")
        print("1. Check URL Chunk")
        print("2. Total Number of Chunks and Range")
        print("3. Print Chunk URLs(saves the file in the same directory as the manifest)")
        print("4. Exit")
       
        choice = int(input("Enter your choice: "))

        if choice == 1:
            manifest_path = input("Enter the path to the DASH manifest XML: ")
            url = input("Enter the URL to check: ")
            print(check_url_chunk(url, manifest_path))
        elif choice == 2:
            manifest_path = input("Enter the path to the DASH manifest XML: ")
            print(total_chunks(manifest_path))
        elif choice == 3:
            manifest_path = input("Enter the path to the DASH manifest XML: ")
            print_chunk_urls(manifest_path)
        elif choice == 4:
            break
        else:
            print("Invalid choice. Please try again.")
