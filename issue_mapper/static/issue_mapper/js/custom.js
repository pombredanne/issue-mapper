(function($){
    
    window.issue_mapper = {
        COOKIE_BUTTONS_FLOAT: null,
        deleteAllCookies: function(){
            var cookies = document.cookie.split(";");
            for (var i = 0; i < cookies.length; i++) {
                var cookie = cookies[i];
                var eqPos = cookie.indexOf("=");
                var name = eqPos > -1 ? cookie.substr(0, eqPos) : cookie;
                document.cookie = name + "=;expires=Thu, 01 Jan 1970 00:00:00 GMT";
            }
        },
        
        update_footer_position: function(){
        	var footer = $('#footer');
            var body = $('body');
            var win = $(window);//$(this); //this = window
            if(win.height() > footer.position().top+footer.height()){
                //footer.addClass('footer-fixed');
                body.addClass('footer-fixed');
            }
        },
        
        isValidDate: function(value, userFormat){
            var userFormat = userFormat || 'mm/dd/yyyy';
            var delimiter = /[^mdy]/.exec(userFormat)[0];
            var theFormat = userFormat.split(delimiter);
            var theDate = value.split(delimiter);
            var isDate = function (date, format){
                var m, d, y
                for (var i = 0, len = format.length; i < len; i++) {
                    if (/m/.test(format[i])) m = date[i]
                    if (/d/.test(format[i])) d = date[i]
                    if (/y/.test(format[i])) y = date[i]
                }
                return (
                    m > 0 && m < 13 &&
                    y && y.length === 4 &&
                    d > 0 && d <= (new Date(y, m, 0)).getDate()
                )
            }
            return isDate(theDate, theFormat);
        },
        
        bind_inline_link_voters: function(){
            
            $('.real-issue-tag:not([stats-bound])').each(function(){
                var el = $(this);
                el.attr('stats-bound', true);
                el.bind('mouseover', $.debounce(100, function(){
                    var el = $(this);
                    $('.tag-stats', el).fadeIn('fast').css("display","inline-block");
                }));
                el.bind('mouseout', $.debounce(500, function(){
                    var el = $(this);
                    $('.tag-stats', el).fadeOut('fast');
                }));
            });
            
            $('.change-context-filter:not([qtip-bound])').each(function(i){
                var el = $(this);
                el.attr('qtip-bound', true);
                el.qtip({
                    suppress: true,
                    content:{
                        text: function(event, api){
                            var element = $(this);
                            $.ajax({
                                url: element.data('url')
                            })
                            .then(function(content){
                                api.set('content.text', content);
                                //window.issue_mapper.bind_inline_link_voters();
                            }, function(xhr, status, error) {
                                // Upon failure... set the tooltip content to the status and error value
                                api.set('content.text', status + ': ' + error);
                            });
                            return 'Loading...';
                        }
                    },
                    show:{
                        //event: 'click'
                        solo: true
                    },
                    hide:{
                        //event: 'click mouseleave',
                        delay: 3000,
                        fixed: true
                    },
                    position:{
                        my: 'top left',
                        at: 'bottom center',
                        corner: 'rightMiddle',
                        adjust: {
                            method: 'flip'
                        }
                    },
                    style:{
                        tip: { corner:true },
                        //def:false,
                        classes: 'qtip-light qtip-shadow custom-tag-qtip shadow'
                    }
                });
            });

            // Bind supports yes/no voter buttons.
            $('a.support-voter:not([bound])').each(function(i){
                var el = $(this);
                el.attr('bound', true);
                el.click(function(){
                    var el = $(this);
                    var url = el.attr('ajax-url');
                    $.ajax({url: url})
                    .then(function(content){
                        // Success!
                        if(content.weight == 1){
                            el.removeClass('btn-default');
                            el.addClass('btn-primary');
                        }else{
                            el.addClass('btn-default');
                            el.removeClass('btn-primary');
                        }
                    }, function(xhr, status, error) {
                        // Failure!
                        //api.set('content.text', status + ': ' + error);
                        //TODO
                    });
                });
            });
            
            $('li.real-tag a:not([qtip-bound])').each(function(i){
                var el = $(this);
                el.attr('qtip-bound', true);
                el.qtip({
                    suppress: true,
                    content:{
                        text: function(event, api){
                            var element = $(this);
                            $.ajax({
                                url: element.data('url')
                            })
                            .then(function(content){
                                api.set('content.text', content);
                                window.issue_mapper.bind_inline_link_voters();
                            }, function(xhr, status, error) {
                                // Upon failure... set the tooltip content to the status and error value
                                api.set('content.text', status + ': ' + error);
                            });
                            return 'Loading...';
                        }
                    },
                    show:{
                        //event: 'click'
                        solo: true
                    },
                    hide:{
                        event: 'click mouseleave',
                        delay: 1000,
                        fixed: true
                    },
                    position:{
                        my: 'top center',
                        at: 'bottom center',
                        corner: 'rightMiddle',
                        adjust: {
                            method: 'flip'
                        }
                    },
                    style:{
                        tip: { corner:true },
                        //def:false,
                        classes: 'qtip-light qtip-shadow custom-tag-qtip shadow'
                    }
                });
            });
            
            $("li.quotes a:not([bound])").each(function(i){
                var el = $(this);
                el.attr('bound', true);
                el.click(function(){
                    var el = $(this);
                    var parent = el.parent().parent().parent();
                    var quotes = $('.quotes-list', parent);
                    var url = el.attr('data-url');
                    if(quotes.length){
                        quotes.toggle();
                        return false;
                    }
                    $.ajax({
                        url:url,
                        dataType:'html',
                        success:function(html, textStatus, jqXHR){
                            var content = $('<div/>').html(html).contents();
                            parent.append(content);
                        }
                    });
                    return false;
                });
            });
            
            $("i.vote-link:not([bound])").each(function(i){
                /* Record the user's vote when they click an up/down vote
                 * link. */
                var el = $(this);
                el.attr('bound', true);
                el.click(function(){
                    var el = $(this);
                    var link_id = el.parent().attr('link-id');
                    var parent = el.parent();
                    var vote_type = (el.hasClass('upvote-link'))?'upvote':'downvote';
                    var vote_url = el.attr('vote-url');
                    $.ajax({
                        url:vote_url,
                        dataType:'html',
                        success:function(data, textStatus, jqXHR){
                            parent.replaceWith($(data));
                            // Rebind new element.
                            window.issue_mapper.bind_inline_link_voters();
                        }
                    });
                });
            });
        },
        bind_ajax_cross_links: function(){
            $('.ajax-search-results .ajax-link:not([bound])').each(function(i){
                /* Show search results when a user enters text on a focussed
                 * search field. */
                var el = $(this);
                el.attr('bound', true);
                el.click(function(e){
                    e.preventDefault();
                    var el = $(this);
                    var issue = el.attr('issue_id');
                    var person = el.attr('person_id');
                    var link_id = el.attr('link_id');
                    var url = el.attr('cross-link-url');
                    $.ajax({
                        url:url,
                        type:'GET',
                        data:{
                            link_id:link_id,
                            issue:issue,
                            person:person
                        },
                        dataType:'json',
                        success:function(data, textStatus, jqXHR){
                            if(data.success){
                                window.open(data.url, '_blank');
                            }else{
                            }
                        }
                    });
                    return false;
                });
            });
        },
        bind_comment_forms: function(){

            $('.comment-reply-show:not([bound])').each(function(i){
                var el = $(this);
                el.attr('bound', true);
                el.click(function(e){
                    var el = $(this);
                    var parent = $(el.parent().parent().parent());
                    var comment_form = $('.comment-form-container:first', parent);
                    comment_form.slideToggle(400, function(){
                        var el = $(this);
                        $(':input:visible:first', el).focus();
                    });
                    e.preventDefault();
                    return false;
                });
            });

            $('.comment:not([bound])').each(function(i){
                var container = $(this);
                container.attr('bound', true);
                
                $('.comment-delete:first', container).click(function(e){
                    e.preventDefault();
                    var el = $(this);
                    el.hide();
                    $('.comment-delete-confirm:first', el.parent()).show();
                    return false;
                });
                
                $('.comment-delete-no:first', container).click(function(e){
                    e.preventDefault();
                    var el = $(this);
                    var parent = el.parent().parent();
                    $('.comment-delete:first', parent).show();
                    $('.comment-delete-confirm:first', parent).hide();
                    return false;
                });
                
                $('.comment-delete-yes:first', container).click(function(e){
                    e.preventDefault();
                    var el = $(this);
                    var parent = el.parent().parent();
                    //$('.comment-delete:first', parent).show();
                    //$('.comment-delete-confirm:first', parent).hide();
                    var url = el.attr('url');
                    $.ajax({
                        url:url,
                        success:function(data){
                            comment_id = data.comment_id;
                            var comment = $('.comment[comment_id='+comment_id+']');
                            $('.comment-commenter:first', comment).html('[deleted]').addClass('muted');
                            $('.comment-content:first', comment).html('[deleted]').addClass('muted');
                        }
                    });
                    return false;
                });
            });
            
            $('.comment-form-container:not([bound])').each(function(i){
                var container = $(this);
                container.attr('bound', true);
                var comment_form_id = container.attr('comment_form_id');

                $('.new-comment-field:first', container).keypress(function(){
                    var el = $(this);
                    var maxlength = parseInt(el.attr('maxlength'));
                    var val = el.val();
                    var val_length = val.length;
                    $('.new-comment-maxlength-notice', container).html('');
                    if(val_length){
                        $('.new-comment-maxlength-notice', container).html(maxlength-val_length + ' characters remaining');
                    }
                });
                
                $('.new-comment-submit-button:first', container).click(function(){
                    var comment = $('.new-comment-field', container);
                    var maxlength = parseInt(comment.attr('maxlength'));
                    var text = $.trim(comment.val()).slice(0, maxlength);
                    if(!text.length){
                        return false;
                    }
                    $.ajax({
                        url:comment.attr('url'),
                        data:{
                            comment:text
                        },
                        type:'get',
                        dataType:'json',
                        success:function(data, textStatus, jqXHR){
                            if(data.success){
                                $('.new-comment-field', container).val('');
                                $('.new-comment-maxlength-notice', container).html('');
                                var content = $('<div/>').html(data.html).contents();
                                //$('.comment-replies:first', container.parent()).prepend(content);
                                $('.comment-form-container:first', container.parent()).after(content);
                                window.issue_mapper.bind_comment_forms();
                                if(container.attr('comment_form_id') != $('.comment-form-container:first').attr('comment_form_id')){
                                    container.slideToggle();
                                }
                            }else{
                                $('.new-comment-maxlength-notice', container).html(data.message);
                            }
                        }
                    });
                    return false;
                });
            });
        }
    };
    
    $(document).ready(function($){
        
        var footer = $('#footer');
        var body = $('body');
        
        $(window).on('resize', window.issue_mapper.update_footer_position);
        
        $('#keyword-search-box').change(function(){
            var el = $(this);
            qs = $.query.set('q', el.val()).set('page', '1').remove('nst');
            window.location.href = qs;
        });
        
        // Support loading old links via ajax.
        $('.show-older-links-btn').click(function(){
            var el = $(this);
            var url = el.attr('url');
            el.html('loading...');
            $.ajax({
                url:url,
                dataType:'html',
                success:function(data, textStatus, jqXHR){
                    var content = $('<div/>').html(data).contents();
                    el.replaceWith(content);
                    window.issue_mapper.bind_inline_link_voters();
                }
            });
            return false;
        });
        
        $('.position-sparkline:not([bound])').each(function(i){
            var el = $(this);
            el.attr('bound', true);
            var points = el.attr('data').split(',');
            points = points.reduce(function(ids, id){
                ids.push(parseInt(id));
                return ids;
            }, []);
            var colors = el.attr('colors').split(',');
            el.sparkline(points, {
                type: 'pie',
                width: '25',
                height: '25',
                sliceColors: colors
            });
        });
        
        function submit_issue_link(){
            var submit_url = $('#new-link-section').attr('url');
            var url_field = $('#new-link-section [name=url]');
            var new_url = url_field.val();
            if(!new_url){
                url_field.addClass('error');
                return false;
            }
            $('#new-link-section .url-error').html('');
            url_field.removeClass('error');
            $.ajax({
                url:submit_url,
                data:{url:new_url},
                dataType:'json',
                success:function(data, textStatus, jqXHR){
                    if(data.success){
                        url_field.removeClass('error');
                        url_field.val('');
                        if(data.html.length){
                            var content = $('<div/>').html(data.html).contents();
                            $('#insert-new-links-point').before(content);
                            window.issue_mapper.bind_inline_link_voters();
                        }
                    }else{
                        url_field.addClass('error');
                        var message = 'Invalid URL.';
                        if(data.message){
                            message = data.message;
                        }
                        $('#new-link-section .url-error').html(message);
                    }
                }
            });
            return false;
        }
        $('#new-link-section button[type=submit]').click(submit_issue_link);
        $('#new-link-section [name=url]').keydown(function(e){
            var code = (e.keyCode ? e.keyCode : e.which);
            if(code == 13){
                e.preventDefault();
                submit_issue_link();
                return false;
            }
        });
        
        $('.add-url-btn').click(function(e){
            e.preventDefault();
            $('#new-link-section').slideToggle();
            return false;
        });
        
        // Clear sticky search parameters when the home link is clicked.
        $('.page-header .name a').click(function(e){
            e.preventDefault();
            $.cookie('qt', '');
            $.cookie('keywords', '');
            window.location.href = $(this).attr('href');
            return false;
        });
        
        /* Update the page URL when a new search filter is selected. */
        $('.search-list-right select:not([no-auto-update])').change(function(){
            var el = $(this);
            var val = el.val();
            qs = $.query.set('page', '1');
            if(val==''){
                qs = qs.remove(el.attr('name'));
            }else{
                qs = qs.set(el.attr('name'), val);
            }
            qs = qs.remove('nst');
            window.location.href = qs;
        });
        
        $('#update-search-results').click(function(e){
            e.preventDefault();
            var fields = $('.search-list-right select');
            qs = $.query.set('page', '1');
            qs = qs.remove('nst');
            for(var i=0; i<fields.length; i+=1){
                var field = $(fields[i]);
                var val = field.val();
                if( Object.prototype.toString.call( val ) === '[object Array]' ) {
                    val = val.join(',');
                }
                var name = field.attr('name');
                if(val==''){
                    qs = qs.remove(name);
                }else{
                    qs = qs.set(name, val);
                }
            }
            window.location.href = qs;
            return false;
        });
        
        $('.person-summary-lower-toggle').click(function(){
            var el = $(this);
            $('.person-summary-lower').slideToggle(400, function(){
                var el = $(this);
                if(el.is(":visible")){
                    $('.person-summary-lower-toggle i').addClass('icon-chevron-up');
                    $('.person-summary-lower-toggle i').removeClass('icon-chevron-down');
                }else{
                    $('.person-summary-lower-toggle i').removeClass('icon-chevron-up');
                    $('.person-summary-lower-toggle i').addClass('icon-chevron-down');
                }
            });
        });
        
        $('.inline-motion-button').click(function(){
            var el = $(this);
            var attribute = el.attr('attribute');
            var url = el.attr('url');
            $.ajax({
                url:url,
                dataType:'json',
                success:function(data, textStatus, jqXHR){
                    if(data.vote_total != null){
                        $('.vote-to-'+attribute+'-count').html(data.vote_total);
                    }
                    if(data.vote_class == 'up'){
                        $('.up[attribute="'+attribute+'"]').addClass('inline-motion-button-selected');
                        $('.up[attribute="'+attribute+'"]').attr('title', data.description);
                        $('.down[attribute="'+attribute+'"]').removeClass('inline-motion-button-selected');
                        $('.down[attribute="'+attribute+'"]').attr('title', data.description);
                    }else{
                        $('.up[attribute="'+attribute+'"]').removeClass('inline-motion-button-selected');
                        $('.up[attribute="'+attribute+'"]').attr('title', data.description);
                        $('.down[attribute="'+attribute+'"]').addClass('inline-motion-button-selected');
                        $('.down[attribute="'+attribute+'"]' ).attr('title', data.description);
                    }
                }
            });
        });
        
        $('.button-float-control-down').click(function(){
            var el = $(this);
            el.hide();
            $('.button-float-control-up').show();
            $('#issue-container .buttons').addClass('buttons-fixed-bottom');
            $.cookie(window.issue_mapper.COOKIE_BUTTONS_FLOAT, 1);
        });
        
        $('.button-float-control-up').click(function(){
            var el = $(this);
            el.hide();
            $('.button-float-control-down').show();
            $('#issue-container .buttons').removeClass('buttons-fixed-bottom');
            $.cookie(window.issue_mapper.COOKIE_BUTTONS_FLOAT, 0);
        });
        
        function save_position(el, importance){
            var url = el.attr('url');
            var polarity = $('#id_polarity').val();
            var issue = $('#id_issue').val();
            var person = $('#id_person').val();
            $.ajax({
                url:url,
                data:{
                    polarity:polarity,
                    importance:importance,
                    issue:issue,
                    person:person
                },
                dataType:'json',
                type:'GET',
                success:function(data, textStatus, jqXHR){
                    if(data.success){
                        $('.buttons label').removeClass('selected');
                        $('label[for="importance_'+data.importance+'"]').addClass('selected');
                        if(data.next_url){
                            window.location.href = data.next_url;
                        }
                    }
                }
            });
        }
        
        $('button.issue-answer-button').click(function(e){
            e.preventDefault();
            var el = $(this);
            var is_final = el.attr('final');
            if(el.hasClass('selected')){
                if($('.slide-out-options').is(":visible")){
                    el.removeClass('selected');
                    $('#id_polarity').val('');
                    $('.slide-out-options').slideUp();
                }else{
                    $('.slide-out-options').slideDown();
                }
            }else{
                $('button.issue-answer-button').removeClass('selected');
                el.addClass('selected');
                $('#id_polarity').val(el.val());
                $('.slide-out-options').slideDown();
                if(is_final){
                    // Save position if no importance allowed.
                    save_position(el, '');
                }
            }
            return false;
        });
        
        //TODO:Record position on other person.
        
        // Record importance.
        $('.importance-option').click(function(e){
            var el = $(this);
            var importance = el.val();
            save_position(el, importance);
        });
        
        $('#cross-link-person').keydown($.debounce(500, function(){
            var el = $(this);
            var url = el.attr('url');
            var link_id = el.attr('link_id');
            var person_id = el.attr('person_id');
            var issue_id = el.attr('issue_id');
            var content = $.trim(el.val());
            if(!content.length){
                $('.ajax-person-search-results').remove();
                return;
            }
            $.ajax({
                url:url,
                type:'GET',
                data:{
                    content:content
                },
                dataType:'html',
                success:function(data, textStatus, jqXHR){
                    $('.ajax-person-search-results').remove();
                    var content = $('<div/>').html(data).contents();
                    el.after(content);
                    $('.ajax-person-search-results').width(el.width()).hide();
                    $('.ajax-person-search-results .ajax-link').attr('link_id', link_id);
                    if(person_id){
                        $('.ajax-person-search-results .ajax-link').attr('person_id', person_id);
                    }
                    if(issue_id){
                        $('.ajax-person-search-results .ajax-link').attr('issue_id', issue_id);
                    }
                    window.issue_mapper.bind_ajax_cross_links();
                    $('.ajax-person-search-results').fadeIn();
                }
            });
        }))
        .focus(function(){
            $('.ajax-person-search-results').fadeIn();
        })
        .blur(function(){
            $('.ajax-person-search-results').fadeOut();
        });
        
        $('#cross-link-issue').keydown($.debounce(500, function(){
            var el = $(this);
            var url = el.attr('url');
            var link_id = el.attr('link_id');
            var person_id = el.attr('person_id');
            var issue_id = el.attr('issue_id');
            var content = $.trim(el.val());
            if(!content.length){
                $('.ajax-issue-search-results').remove();
                return;
            }
            $.ajax({
                url:url,
                type:'GET',
                data:{
                    content:content
                },
                dataType:'html',
                success:function(data, textStatus, jqXHR){
                    $('.ajax-issue-search-results').remove();
                    var content = $('<div/>').html(data).contents();
                    el.after(content);
                    $('.ajax-issue-search-results').width(el.width()).hide();
                    $('.ajax-issue-search-results .ajax-link').attr('link_id', link_id);
                    if(person_id){
                        $('.ajax-search-results .ajax-link').attr('person_id', person_id);
                    }
                    if(issue_id){
                        $('.ajax-search-results .ajax-link').attr('issue_id', issue_id);
                    }
                    window.issue_mapper.bind_ajax_cross_links();
                    $('.ajax-issue-search-results').fadeIn();
                }
            });
        }))
        .focus(function(){
            $('.ajax-issue-search-results').fadeIn();
        })
        .blur(function(){
            $('.ajax-issue-search-results').fadeOut();
        });
        
        window.issue_mapper.bind_inline_link_voters();
        window.issue_mapper.bind_comment_forms();
        window.issue_mapper.bind_ajax_cross_links();
        window.issue_mapper.update_footer_position();
        
	    $('.panel-open-close-button').click(function(){
	        var el = $(this);
	        var body = $('.panel-body', el.parent().parent());
	        body.slideToggle(function(){
		        if(body.is(":visible")){
		        	el.addClass(el.attr('close-icon'));
		        	el.removeClass(el.attr('open-icon'));
		        }else{
		        	el.removeClass(el.attr('close-icon'));
		        	el.addClass(el.attr('open-icon'));
		        }
	        });
	        return false;
	    });
	    
    });
    
})(jQuery);