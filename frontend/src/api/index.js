import { formatDistance } from "date-fns";

const debug = true
const testData = {
    "title": "Wee Media Receiver",
    "debug": false,
    "version": "0.0.2",
    "openapi_url": "string",
    "status": {
        "NOTIFIED": 3,
        "UPLOADED": 1,
    },
    "last_update": "2022-06-14T11:21:32",
    "release": "2022-06-14T11:21:39",
    "started_time": "2022-06-20T11:23:24.731214",
    "s3_url": "string",
    "latest_media": [
        {
            "media_id": "videos/2022/06/bomperfil_1faf29080d270a0d126a4e6737bf058b.mp4",
            "new_media_id": "videos/2022/06/bomperfil_1faf29080d270a0d126a4e6737bf058b.mp4",
            "status": "NOTIFIED",
            "post_id": 1,
            "metadata": {
                "drawings": 22.9652,
                "hentai": 1.026,
                "neutral": 71.34230000000001,
                "porn": 3.1109,
                "sexy": 1.5556
            }
        },
        {
            "media_id": "videos/2022/06/bomperfil_1faf29080d270a0d126a4e6737bf058b.mp4",
            "new_media_id": "videos/2022/06/bomperfil_1faf29080d270a0d126a4e6737bf058b.webm",
            "status": "NOTIFIED",
            "post_id": 2,
            "metadata": {
                "drawings": 20.9652,
                "hentai": 1.026,
                "neutral": 31.34230000000001,
                "porn": 3.1109,
                "sexy": 1.5556
            }
        }
    ]
}
export const fetchApi = async function () {
    let response = {}
    try {
        if (debug) {
            console.debug('fetchApi', 0)
            response = testData
        } else {
            const req = await fetch("/stats")
            response = await req.json()
        }
        response.title = `${response.title} v${response.version}`
        response.subtitle = `release ${new Date(response.release).toLocaleDateString()} | running for ${formatDistance(
            new Date(),
            new Date(response.started_time))}`;
        console.info('fetchApi', response)
        return response
    } catch (error) {
        console.error('fetchApi', error)

    }
    return {}
}

export const parseMedia = function (media, baseUrl) {
    let mediaId, mediaIdLink

    if (media.new_media_id && media.new_media_id != media.media_id) {
        mediaId = `${media.media_id} -> ${media.new_media_id}`
        mediaIdLink = `<a href="${baseUrl}/${media.new_media_id}">${media.new_media_id}</a>`

    } else {
        mediaId = `${media.media_id}`
        mediaIdLink = `<a href="${baseUrl}/${media.media_id}">${media.media_id}</a>`
    }



    const cat = [];
    for (const key in media.metadata) {
        cat.push({
            label: key,
            value: Math.round(parseFloat(media.metadata[key]) * 100) / 100,
        });
    }
    cat.sort((a, b) => b.value - a.value);
    const categories = cat.map(c => `${c.label}: ${c.value}`).join('\n');

    return {
        postId: media.post_id,
        mediaId: mediaId,
        status: media.status,
        categories: categories,
        mediaIdLink: mediaIdLink,
    }

}

function getFilename (fullPath) {
    return fullPath.replace(/^.*[\\\/]/, '');
}