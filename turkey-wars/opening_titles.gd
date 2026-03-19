extends Control

@onready var title_label: Label = $CenterContainer/TitleLabel


func _ready() -> void:
	title_label.modulate.a = 0.0

	var tween := create_tween()
	tween.tween_property(title_label, "modulate:a", 1.0, 1.0)
	tween.tween_interval(3.0)
	tween.tween_property(title_label, "modulate:a", 0.0, 1.0)