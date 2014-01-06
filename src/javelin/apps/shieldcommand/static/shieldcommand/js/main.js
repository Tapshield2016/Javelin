function classList(elem){
   var classList = elem.attr('class').split(/\s+/);
    var classes = new Array(classList.length);
    $.each( classList, function(index, item){
        classes[index] = item;
    });

    return classes;
}

$(window).resize(function () {
    var h = $(window).height();
    offsetTop = 50; // Calculate the top offset

    $('#map-canvas').css('height', (h - offsetTop));
    $('#profile').css('height', (h - offsetTop));
	var tabsHeight = $('.accordion-panel-heading').outerHeight() * $('.accordion-panel-heading').length;
	var height = $('#accordion').innerHeight() - tabsHeight;
	$('#accordion div.accordion-panel-body').height(height);
}).resize();

$('li.alert').click(function(e) {
    var target = $(e.target);

    if (Javelin.activeAlertTarget) {
		Javelin.activeAlertTarget.removeClass('selected');
    };
	Javelin.activeAlertTarget = target;
	Javelin.activeAlertTarget.addClass('selected');

    var map = $('#map-canvas');
    var profile = $('#profile');
    classes = classList(map);
    for (var i = 0; i < classes.length; i++) {
    	if(classes[i] == 'col-md-12') {
    		map.removeClass('col-md-12').addClass('col-md-9');
    		profile.removeClass('hidden').addClass('col-md-3');
    		break;
    	}
    	else if (classes[i] == 'col-md-9') {
    		map.removeClass('col-md-9').addClass('col-md-12');
    		profile.removeClass('col-md-3').addClass('hidden');
    		break;
    	}
    };

});

function csrfSafeMethod(method) {
    // these HTTP methods do not require CSRF protection
    return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
}

function getCookie(name) {
    var cookieValue = null;
    if (document.cookie && document.cookie != '') {
        var cookies = document.cookie.split(';');
        for (var i = 0; i < cookies.length; i++) {
            var cookie = jQuery.trim(cookies[i]);
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) == (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

var csrftoken = getCookie('csrftoken');

$.ajaxSetup({
    crossDomain: false, // obviates need for sameOrigin test
    beforeSend: function(xhr, settings) {
        if (!csrfSafeMethod(settings.type)) {
            xhr.setRequestHeader("X-CSRFToken", csrftoken);
        }
    }
});

$(document).ajaxError(function(event, jqxhr, settings, exception) {
    console.log("Error: " + exception);
});

$('#accordion').on('hidden.bs.collapse', function (event) {
    setTimeout(function() {
        if ($('.panel-collapse.in').length == 0) {
            $('.accordion-default').click();
        }
    }, 400);
});

var newAlertSound = new buzz.sound("/media/static/shieldcommand/sounds/new_alert", {
    formats: ["mp3", "wav",],
    preload: true,
});


var newChatSound = new buzz.sound("/media/static/shieldcommand/sounds/new_chat", {
    formats: ["mp3", "wav",],
    preload: true,
});
