
    $.ready(function() {
    $('.follow-button').click(function() {
        var $this = $(this);
        var post_id = this.id;
        $.post('/post/' + id + '/follow', function() {
            $this.replaceWith("<span class='followed'>followed</span>");
        });
    });
});
