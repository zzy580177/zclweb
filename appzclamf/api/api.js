import request from '@/utils/request'
export function get_cell_liveStatus(data){
    return request({
        url:'/api/livestats/<cellaId>',
        method :'get',
        data
    })
}

export function getPezzi(data){
    return request({
        url:'/api/Pezzi/<cellaId>',
        method :'get',
        data
    })
}

export function getStato(data){
    return request({
        url:'/api/Stato/<cellaId>',
        method :'get',
        data
    })
}