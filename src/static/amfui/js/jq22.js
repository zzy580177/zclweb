$.fn.zoom_img = function(options){
    $t = this;
    if($t.length>1){
        $t.each(function(){
            $(this).zoom_img(options);
        })
        return $t;
    }
    var ops = {
        width:50,
        height:28
    }

    $t.css("position","relative");
     ops = $.extend(ops,options);

    if($t.attr("_width")){
         ops.width = window.parseInt($t.attr("_width"));
         ops.height = window.parseInt( $t.attr("_height"));
    }

     var _left = ops.width/2;
     var _top = ops.height/2;
     var width = $(this).width();
     var height = $(this).height();

     if(width<1){
         var img = new Image()
         img.src = $t.attr("src");
         img.onload = function(){ //图片真实宽高
            width = img.width;
            height = img.height;
         }
    }
     $t.hover(function(){
        var img=$(this);
        img.stop(true).animate({
            width:width+ops.width,
            height:height+ops.height,
            left:-_left,
            top:-_top
        },500);

    },function(){
        $(this).stop(true).animate({
            width:width,
            height:height,
            left:0,
            top:0
        },500);
    });

     return $t;
}


var edu=function(){

    var edu_ul=$(".about_edulist ul");
    var edu_li=edu_ul.children("li");
    var edu_w=edu_li.width();
    var edu_tm=600;

    edu_ul.hover(function(){
        window.clearInterval(t);
    },function(){
        timer();
    });

    var leftbtn=function(){
        edu_li=edu_ul.children("li");
        edu_li.last().prependTo(edu_ul);
        edu_ul.css("left",-edu_w);
        edu_ul.stop(true).animate({
            left:0
        },edu_tm);
    }
    var rgbtn=function(){
        edu_li=edu_ul.children("li");
        edu_ul.stop(true).animate({
            left:-edu_w
        },edu_tm,function(){
            edu_li.first().appendTo(edu_ul);
            edu_ul.css("left",0)
        });
    }

    $(".edu_leftbtn").click(function(){
        timer();
        leftbtn();
    });
    $(".edu_rgbtn").click(function(){
        timer();
        rgbtn();
    });

    var t=null;
    var timer=function(){
        window.clearInterval(t);
        t=window.setInterval(function(){
            rgbtn();
        },40000000);
    };
    timer();

}