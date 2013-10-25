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
        	triple_id: 0,
        	// The default context to use when searching.
        	context_id: 0,
        	// The URL to use to retrieve JSON formatted triple data.
        	get_triple_url: '?',
        	// The URL to use to perform plaintext search of triples.
        	search_triple_url: '?',
        	// The URL to use to perform plaintext search of senses.
        	search_sense_url: '?',
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