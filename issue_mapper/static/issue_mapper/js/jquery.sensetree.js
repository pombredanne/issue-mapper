/*
$('#test').sensetree();
var myplugin = $('#test').data('myplugin');
myplugin.publicMethod(); // prints "publicMethod() called!" to console
 * */
(function($){
    
    var Triple = function(s_id, p_id, o_id){
        this.s_id = s_id;
        this.p_id = p_id;
        this.o_id = o_id;
    }
    
    var SenseTree = function(element, options){
        var elem = $(element);
        var obj = this;
        
        // Merge options with defaults
        var settings = $.extend({
            // The initial triple to display.
            // If no id provided, a blank triple creation form will be shown instead.
            triple_id_list: [],
            //triple_id: 0,
            // The default context to use when searching.
            context_id: 0,
            // The URL to use to retrieve JSON formatted triple data.
            get_triple_url: '',
            // The URL to use to create a new triple.
            create_triple_url: '',
            // The URL to use to perform plaintext search of triples.
            search_triple_url: '',
            // The URL to use to perform plaintext search of senses.
            search_sense_url: '',
            // Extra data to send in all ajax requests.
            search_all_url: '',
            extra: {},
            // Allow editing.
            allow_editing: true,
            default_ul_classes: "list-group",
            default_li_classes: "list-group-item",
            param: 'defaultValue'
        }, options || {});
        
        // Public method
        this.publicMethod = function(){
            console.log('publicMethod() called!');
        };
        
        // Private method - can only be called from within this object
        var privateMethod = function(){
            console.log('private method called!');
        };
        
        var bind_highlights = function(){
            $('.in-line-editable:not([bound])', element).each(function(i){
                var el = $(this);
                el.attr('bound', true);
                el.bind('mouseover', function(){
                    var el = $(this);
                    $('[data-pk="'+el.data('pk')+'"]').addClass('sense-highlight');
                });
                el.bind('mouseout', function(){
                    var el = $(this);
                    $('[data-pk="'+el.data('pk')+'"]').removeClass('sense-highlight');
                });
            });
        };
        
        var element = $(element);
        element.addClass(settings.default_ul_classes);
        
        var add_form = null;
        if(settings.allow_editing){
            var add_form = $(
                '<li class="list-group-item muted">'+
                '<form class="new-triple-form form-inline">&nbsp;'+
                '<input class="form-control" name="subject" type="text" placeholder="subject" value="" real-value="" />&nbsp;'+
                '<input class="form-control" name="predicate" type="text" placeholder="predicate" value="" real-value="" />&nbsp;'+
                '<input class="form-control" type="text" name="object" placeholder="object" value="" real-value="" />&nbsp;'+
                '<button type="submit" class="btn btn-default btn-primary save-button">Add Statement</button></form></li>')
            add_form.prependTo(element);
            
            $("[name=subject]", element).autocomplete({
                source: settings.search_all_url,
                minLength: 2,
                focus: function(event, ui){
                    var el = $(this);
                    el.val(ui.item.label);
                    el.attr('real-value', ui.item.value);
                    return false;
                },
                change: function(event, ui){
                    var el = $(this);
                    if(ui && ui.item){
                        el.val(ui.item.label);
                        el.attr('real-value', ui.item.value);
                    }else{
                        el.attr('real-value', '');
                    }
                },
                select: function(event, ui){
                    var el = $(this);
                    el.val(ui.item.label);
                    el.attr('real-value', ui.item.value);
                    return false;
                }
            });

            $("[name=object]", element).autocomplete({
                source: settings.search_all_url,
                minLength: 2,
                focus: function(event, ui){
                    var el = $(this);
                    el.val(ui.item.label);
                    el.attr('real-value', ui.item.value);
                    return false;
                },
                change: function(event, ui){
                    var el = $(this);
                    if(ui && ui.item){
                        el.val(ui.item.label);
                        el.attr('real-value', ui.item.value);
                    }else{
                        el.attr('real-value', '');
                    }
                },
                select: function(event, ui){
                    var el = $(this);
                    el.val(ui.item.label);
                    el.attr('real-value', ui.item.value);
                    return false;
                }
            });
        }
        
        $.ajax({
            url:settings.get_triple_url,
            dataType:'html',
            method:'post',
            data:$.extend({
                ids:settings.triple_id_list.join(',')
            }, settings.extra || {}),
            success:function(html){
                var content = $('<div/>').html(html).contents();
                if(add_form){
                    $(content).insertAfter(add_form);
                }else{
                    element.append(content);
                }
                bind_highlights();
            }
        });
        
        $('.new-triple-form', element).submit(function(){
            var form = $(this);
            var subject = $('[name=subject]', form);
            var predicate = $('[name=predicate]', form);
            var object = $('[name=object]', form);

            valid = true;
            var subject_text = $.trim(subject.attr('real-value')) || $.trim(subject.val());
            if(!subject_text.length){
                subject.addClass('error');
                valid = false;
            }else{
                subject.removeClass('error');
            }
            var predicate_text = $.trim(predicate.attr('real-value')) || $.trim(predicate.val());
            if(!predicate_text.length){
                predicate.addClass('error');
                valid = false;
            }else{
                predicate.removeClass('error');
            }
            var object_text = $.trim(object.attr('real-value')) || $.trim(object.val());
            if(!object_text.length){
                object.addClass('error');
                valid = false;
            }else{
                object.removeClass('error');
            }
            if(!valid){
                return false;
            }
            var data = $.extend({
                subject_text:subject_text,
                subject_id:subject.data('sense_id'),
                predicate_text:predicate_text,
                predicate_id:predicate.data('sense_id'),
                object_text:object_text,
                object_id:object.data('sense_id')
            }, settings.extra || {});
            $.ajax({
                url:settings.create_triple_url,
                method:'post',
                dataType:'html',
                data:data,
                success:function(html){
                    subject.val('');
                    subject.attr('real-value', '');
                    predicate.val('');
                    object.val('');
                    object.attr('real-value', '');
                    //element.append(data);
                    var content = $('<div/>').html(html).contents();
                    if(add_form){
                        $(content).insertAfter(add_form);
                    }else{
                        element.append(content);
                    }
                }
            });
            return false;
        });
    };
    
    $.fn.sensetree = function(options){
        return this.each(function(){
            var element = $(this);
            
            // Return early if this element already has a plugin instance
            if (element.data('sensetree')) return;

            var sensetree = new SenseTree(this, options);

            // Store plugin object in this element's data
            element.data('sensetree', sensetree);
            
        });
    };
    
})(jQuery);