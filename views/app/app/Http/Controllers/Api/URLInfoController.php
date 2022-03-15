<?php

namespace App\Http\Controllers\Api;

use App\Http\Controllers\Controller;
use Illuminate\Http\Request;
use Exception;
use GuzzleHttp\Client;

class URLInfoController extends Controller
{
    protected $restaurantIdApi = 'https://gappapi.deliverynow.vn/api/delivery/get_from_url?url=';
    protected $getDetailApi = 'https://gappapi.deliverynow.vn/api/delivery/get_detail?id_type=2&request_id=';
    protected $headers = [
        'x-foody-access-token' => true,
        'x-foody-api-version' => 1,
        'x-foody-app-type' => 1004,
        'x-foody-client-id' => true,
        'x-foody-client-language' => 'vi',
        'x-foody-client-type' => 1,
        'x-foody-client-version' => '3.0.0',
    ];

    public function getInfo(Request $request)
    {
        try {
            $deliveryId = $this->getDeliveryId($request->url);

            return $this->getDetail($deliveryId);
        } catch (Exception $e) {
            return null;
        }
    }

    protected function callApi($url)
    {
        $client = new Client();
        $res = $client->get($url, [
            'headers' => $this->headers,
        ]);

        return json_decode($res->getBody()->getContents());
    }

    protected function getDeliveryId($url)
    {
        $urlExplode = explode('https://shopeefood.vn/', $url);
        $shoppePath = count($urlExplode) ? array_pop($urlExplode) : null;
        $res = $this->callApi($this->restaurantIdApi . $shoppePath);

        return $res->reply->delivery_id;
    }

    protected function getDetail($deliveryId)
    {
        $res = $this->callApi($this->getDetailApi . $deliveryId);
        $res = $res->reply->delivery_detail;
        $res->photo = $this->getPhoto($res->photos);

        return $res;
    }

    protected function getPhoto($photos)
    {
        $photo = collect($photos)->first(function ($photo) {
            return in_array($photo->width, [180, 240, 160]);
        });
        if (!$photo) {
            $photo = $photos[floor(count($photos) / 2)];
        }

        return $photo->value;
    }
}
