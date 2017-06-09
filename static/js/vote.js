$(document).ready(function() {

	$(".vote-button").click(function() {
		//Winner
		var id_w = $(this).data('id');
		var cat_w = $(this).data('cat');
		
		//Loser
		var id_l = $(this).parent().parent().siblings('.option-container').find('input').data('id');
		var cat_l = $(this).parent().parent().siblings('.option-container').find('input').data('cat');
		
		var data = {"id_w":id_w, "cat_w":cat_w, "id_l":id_l, "cat_l":cat_l}
		//console.log(data)
		
		$.post("/vote", JSON.stringify(data),
		   	function(reponse){
		   		console.log("Success")
		   		console.log(reponse)
		   		location.reload()
		   	})
    });
});
