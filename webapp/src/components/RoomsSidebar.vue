<template lang="pug">
transition(name="sidebar")
	.c-rooms-sidebar(v-show="show && !snapBack", :style="style", role="navigation", @pointerdown="onPointerdown", @pointermove="onPointermove", @pointerup="onPointerup", @pointercancel="onPointercancel")
		router-link.logo(to="/", v-if="$mq.above['m']", :class="{'fit-to-width': theme.logo.fitToWidth}")
			img(:src="theme.logo.url", :alt="world.title")
		bunt-icon-button#btn-close-sidebar(v-else, @click="$emit('close')") menu
		scrollbars(y)
			.global-links(role="group", aria-label="pages")
				router-link.room(v-if="roomsByType.page.includes(rooms[0])", :to="{name: 'home'}", v-html="$emojify(rooms[0].name)")
				router-link.room(:to="{name: 'schedule'}", v-if="!!world.pretalx && (world.pretalx.url || world.pretalx.domain)") {{ $t('RoomsSidebar:schedule:label') }}
				router-link.room(v-for="page of roomsByType.page", v-if="page !== rooms[0]", :to="{name: 'room', params: {roomId: page.id}}", v-html="$emojify(page.name)")
			.group-title#stages-title(v-if="roomsByType.stage.length || hasPermission('world:rooms.create.stage')")
				span {{ $t('RoomsSidebar:stages-headline:text') }}
				bunt-icon-button(v-if="hasPermission('world:rooms.create.stage')", @click="showStageCreationPrompt = true") plus
			.stages(role="group", aria-describedby="stages-title")
				router-link.stage(v-for="stage, index of roomsByType.stage", :to="stage.room === rooms[0] ? {name: 'home'} : {name: 'room', params: {roomId: stage.room.id}}", :class="{active: stage.room.id === $route.params.roomId, session: stage.session, live: stage.session && stage.room.schedule_data, 'has-image': stage.image, 'starts-with-emoji': startsWithEmoji(stage.room.name)}")
					template(v-if="stage.session")
						img.preview(v-if="stage.image", :src="stage.image")
						.info
							.title {{ $localize(stage.session.title) }}
							.subtitle
								.speakers {{ stage.session.speakers ? stage.session.speakers.map(s => s.name).join(', ') : '' }}
								.room {{ stage.room.name }}
					template(v-else)
						.room-icon(aria-hidden="true")
						.name(v-html="$emojify(stage.room.name)")
			.group-title#chats-title(v-if="roomsByType.videoChat.length || roomsByType.textChat.length || hasPermission('world:rooms.create.chat') || hasPermission('world:rooms.create.bbb')")
				span {{ $t('RoomsSidebar:channels-headline:text') }}
				.buffer
				bunt-icon-button(v-if="hasPermission('world:rooms.create.chat') || hasPermission('world:rooms.create.bbb')", tooltip="Create Channel", :tooltip-fixed="true", @click="showChatCreationPrompt = true") plus
				bunt-icon-button(v-if="worldHasTextChannels", tooltip="Browse all channels", :tooltip-fixed="true", @click="showChannelBrowser = true") compass-outline
			.chats(role="group", aria-describedby="chats-title")
				router-link.video-chat(v-for="chat of roomsByType.videoChat", :to="chat === rooms[0] ? {name: 'home'} : {name: 'room', params: {roomId: chat.id}}", :class="{active: chat.id === $route.params.roomId, 'starts-with-emoji': startsWithEmoji(chat.name)}")
					.room-icon(aria-hidden="true")
					.name(v-html="$emojify(chat.name)")
					i.bunt-icon.activity-icon.mdi(v-if="chat.users === 'many' || chat.users === 'few'", :class="{'mdi-account-group': (chat.users === 'many'), 'mdi-account-multiple': (chat.users === 'few')}", v-tooltip.bottom.fixed="{text: $t('RoomsSidebar:users-tooltip:' + chat.users)}", :aria-label="$t('RoomsSidebar:users-tooltip:' + chat.users)")
				router-link.text-chat(v-for="chat of roomsByType.textChat", :to="chat === rooms[0] ? {name: 'home'} : {name: 'room', params: {roomId: chat.id}}", :class="{unread: hasUnreadMessages(chat.modules[0].channel_id), 'starts-with-emoji': startsWithEmoji(chat.name)}")
					.room-icon(aria-hidden="true")
					.name(v-html="$emojify(chat.name)")
					bunt-icon-button(@click.prevent.stop="$store.dispatch('chat/leaveChannel', {channelId: chat.modules[0].channel_id})") close
				bunt-button#btn-browse-channels-trailing(v-if="worldHasTextChannels", @click="showChannelBrowser = true") {{ $t('RoomsSidebar:browse-channels-button:label') }}
			.group-title#dm-title(v-if="directMessageChannels.length || hasPermission('world:chat.direct')")
				span {{ $t('RoomsSidebar:direct-messages-headline:text') }}
				bunt-icon-button(v-if="hasPermission('world:chat.direct')", tooltip="open a direct message", :tooltip-fixed="true", @click="showDMCreationPrompt = true") plus
			.direct-messages(role="group", aria-describedby="dm-title")
				router-link.direct-message(v-for="channel of directMessageChannels", :to="{name: 'channel', params: {channelId: channel.id}}", :class="{unread: hasUnreadMessages(channel.id)}")
					i.bunt-icon.mdi(v-if="call && call.channel === channel.id", aria-hidden="true").mdi-phone
					.name {{ getDMChannelName(channel) }}
					bunt-icon-button(tooltip="remove", :tooltip-fixed="true", @click.prevent.stop="$store.dispatch('chat/leaveChannel', {channelId: channel.id})") close
			.buffer
			template(v-if="worldHasExhibition && (staffedExhibitions.length > 0 || hasPermission('world:rooms.create.exhibition'))")
				.group-title {{ $t('RoomsSidebar:exhibitions-headline:text') }}
				.admin
					router-link(:to="{name: 'exhibitors'}") {{ $t('RoomsSidebar:exhibitions-manage:label') }}
					router-link(:to="{name: 'contactRequests'}") {{ $t('RoomsSidebar:exhibitions-requests:label') }}
			template(v-if="worldHasPosters && hasPermission('world:rooms.create.poster')")
				.group-title {{ $t('RoomsSidebar:posters-headline:text') }}
				.admin
					router-link(:to="{name: 'posters'}") {{ $t('RoomsSidebar:posters-manage:label') }}
			template(v-if="hasPermission('world:users.list') || hasPermission('world:update') || hasPermission('world:announce') || hasPermission('room:update')")
				.group-title {{ $t('RoomsSidebar:admin-headline:text') }}
				.admin
					router-link.room(:to="{name: 'admin:announcements'}", v-if="hasPermission('world:announce')") {{ $t('RoomsSidebar:admin-announcements:label') }}
					router-link.room(:to="{name: 'admin:users'}", v-if="hasPermission('world:users.list')") {{ $t('RoomsSidebar:admin-users:label') }}
					router-link.room(:to="{name: 'admin:rooms:index'}", v-if="hasPermission('room:update')") {{ $t('RoomsSidebar:admin-rooms:label') }}
					router-link.room(:to="{name: 'admin:config'}", v-if="hasPermission('world:update')") {{ $t('RoomsSidebar:admin-config:label') }}
		router-link.profile(:to="{name: 'preferences'}")
			avatar(:user="user", :size="36")
			.display-name {{ user.profile.display_name }}
			.mdi.mdi-cog
		transition(name="prompt")
			channel-browser(v-if="showChannelBrowser", @close="showChannelBrowser = false", @createChannel="showChannelBrowser = false, showChatCreationPrompt = true")
			create-stage-prompt(v-else-if="showStageCreationPrompt", @close="showStageCreationPrompt = false")
			create-chat-prompt(v-else-if="showChatCreationPrompt", @close="showChatCreationPrompt = false")
			create-dm-prompt(v-else-if="showDMCreationPrompt", @close="showDMCreationPrompt = false")
</template>
<script>
import { mapState, mapGetters } from 'vuex'
import theme from 'theme'
import { startsWithEmoji } from 'lib/emoji'
import Avatar from 'components/Avatar'
import ChannelBrowser from 'components/ChannelBrowser'
import CreateStagePrompt from 'components/CreateStagePrompt'
import CreateChatPrompt from 'components/CreateChatPrompt'
import CreateDmPrompt from 'components/CreateDmPrompt'

export default {
	components: { Avatar, ChannelBrowser, CreateStagePrompt, CreateChatPrompt, CreateDmPrompt },
	props: {
		show: Boolean
	},
	data () {
		return {
			theme,
			lastPointer: null,
			pointerMovementX: 0,
			snapBack: false,
			showChannelBrowser: false,
			showStageCreationPrompt: false,
			showChatCreationPrompt: false,
			showDMCreationPrompt: false
		}
	},
	computed: {
		...mapState(['user', 'world', 'rooms']),
		...mapState('chat', ['joinedChannels', 'call']),
		...mapState('exhibition', ['staffedExhibitions']),
		...mapGetters(['hasPermission']),
		...mapGetters('chat', ['hasUnreadMessages']),
		...mapGetters('schedule', ['sessions', 'currentSessionPerRoom']),
		style () {
			if (this.pointerMovementX === 0) return
			return {
				transform: `translateX(${this.pointerMovementX}px)`
			}
		},
		roomsByType () {
			const rooms = {
				page: [],
				stage: [],
				textChat: [],
				videoChat: []
			}
			for (const room of this.rooms) {
				if (room.modules.length === 1 && room.modules[0].type === 'chat.native') {
					if (!this.joinedChannels.some(channel => channel.id === room.modules[0].channel_id)) continue
					rooms.textChat.push(room)
				} else if (room.modules.some(module => ['call.bigbluebutton', 'call.janus', 'call.zoom'].includes(module.type))) {
					rooms.videoChat.push(room)
				} else if (room.modules.some(module => ['livestream.native', 'livestream.youtube', 'livestream.iframe'].includes(module.type))) {
					let session
					if (this.$features.enabled('schedule-control')) {
						session = this.currentSessionPerRoom?.[room.id]?.session
					}
					// TODO handle session image and multiple speaker avatars
					// const image = session?.speakers.length === 1 ? session.speakers[0].avatar : null
					rooms.stage.push({
						room,
						session,
						// image
					})
				} else {
					rooms.page.push(room)
				}
			}
			return rooms
		},
		directMessageChannels () {
			return this.joinedChannels
				?.filter(channel => channel.members)
				.map(channel => ({
					id: channel.id,
					users: channel.members.filter(member => member.id !== this.user.id)
				}))
				.sort((a, b) => (this.hasUnreadMessages(b.id) - this.hasUnreadMessages(a.id)) || this.getDMChannelName(a).localeCompare(this.getDMChannelName(b)))
		},
		worldHasTextChannels () {
			return this.rooms.some(room => room.modules.length === 1 && room.modules[0].type === 'chat.native')
		},
		worldHasExhibition () {
			return this.rooms.some(room => room.modules.length === 1 && room.modules[0].type === 'exhibition.native')
		},
		worldHasPosters () {
			return this.rooms.some(room => room.modules.length === 1 && room.modules[0].type === 'poster.native')
		},
	},
	methods: {
		getDMChannelName (channel) {
			return channel.users.map(user => user.deleted ? this.$t('User:label:deleted') : user.profile.display_name).join(', ')
		},
		startsWithEmoji (string) {
			return startsWithEmoji(string)
		},
		onPointerdown (event) {
			if (this.$mq.above.m) return
			this.lastPointer = event.pointerId
		},
		onPointermove (event) {
			if (this.$mq.above.m || this.lastPointer !== event.pointerId) return
			this.pointerMovementX += event.movementX / window.devicePixelRatio // because apparently the browser does not do this
			if (this.pointerMovementX > 0) {
				this.pointerMovementX = 0
			}
		},
		async onPointerup (event) {
			if (this.$mq.above.m || this.lastPointer !== event.pointerId) return
			this.lastPointer = null
			if (this.pointerMovementX < -80) {
				this.$emit('close')
			}
			this.pointerMovementX = 0
			// TODO not the cleanest, control transition completely ourselves
			this.snapBack = true
			await this.$nextTick()
			this.snapBack = false
		},
		onPointercancel (event) {
			this.lastPointer = null
			this.pointerMovementX = 0
		}
	}
}
</script>
<style lang="stylus">
.c-rooms-sidebar
	background-color: var(--clr-sidebar)
	display: flex
	flex-direction: column
	min-height: 0
	max-height: var(--vh100)
	.logo
		font-size: 18px
		text-align: center
		margin: 0 16px
		height: 56px
		img
			height: 100%
			max-width: 100%
			object-fit: contain
		&.fit-to-width
			height: auto
			margin: 0
			img
				height: auto
	#btn-close-sidebar
		margin: 8px
		icon-button-style(color: var(--clr-sidebar-text-primary), style: clear)
	> .c-scrollbars
		flex: auto
		.scroll-content
			flex: auto
			color: var(--clr-sidebar-text-primary)
		.scrollbar-rail-y
			.scrollbar-thumb
				background-color: var(--clr-sidebar-text-secondary)
	.global-links
		flex: none
		display: flex
		flex-direction: column
		> *
			ellipsis()
			flex: none
			height: 36px
			line-height: 36px
			padding: 0 24px
			color: var(--clr-sidebar-text-secondary)
			&.router-link-exact-active
				background-color: var(--clr-sidebar-active-bg)
				color: var(--clr-sidebar-text-primary)
			&:hover
				background-color: var(--clr-sidebar-hover-bg)
				color: var(--clr-sidebar-text-primary)
	.group-title
		flex: none
		color: var(--clr-sidebar-text-secondary)
		margin: 16px 8px 0 16px
		height: 28px
		font-weight: 600
		font-size: 12px
		display: flex
		justify-content: space-between
		align-items: center
		.bunt-icon-button
			margin: -4px 0
			icon-button-style(color: var(--clr-sidebar-text-primary), style: clear)
	.emoji
		color: transparent // hide unicode emoji
		display: inline-block
		width: 18px
		height: @width
		vertical-align: text-bottom
		&.needs-space
			margin-right: 4px
	.stages, .chats, .direct-messages, .admin
		flex: none
		display: flex
		flex-direction: column
		> *
			flex: none
			height: 36px
			line-height: 36px
			padding: 0 18px
			color: var(--clr-sidebar-text-secondary)
			display: flex
			position: relative
			&.router-link-exact-active, &.active
				background-color: var(--clr-sidebar-active-bg)
				color: var(--clr-sidebar-text-primary)
			&:hover
				background-color: var(--clr-sidebar-hover-bg)
				color: var(--clr-sidebar-text-primary)
			&.router-link-exact-active, &.active
				.room-icon::before
					color: var(--clr-sidebar-text-secondary)
			.room-icon
				width: 22px
				&::before
					font-family: "Material Design Icons"
					font-size: 18px
					line-height: 34px
					color: var(--clr-sidebar-text-disabled)
					margin: 0 auto
					display: block
					width: 20px

			&.starts-with-emoji
				padding: 0 18px
				// .room-icon
				// 	position: absolute
				// 	width: 18px
				// 	height: @width
				// 	left: 18px
				// 	background-color: var(--clr-sidebar)
				// 	border-radius: 50%
				// 	&::before
				// 		display: block
				// 		height: 18px
				// 		width: 18px
				// 		line-height: @height
				// 		font-size: 14px
				// 		margin: 0 auto
				// .room-icon
				// 	width: 10px
				// .name
				// 	background-color: var(--clr-sidebar)
				// 	padding-left: 3px
				// 	border-radius: 18px
				.room-icon
					display: none
			&.unread
				color: var(--clr-sidebar-text-primary)
				font-weight: 500
				&::after
					content: ''
					position: absolute
					background-color: var(--clr-sidebar-text-primary)
					left: 10px
					top: 15px
					height: 6px
					width: @height
					border-radius: 50%
			.name
				ellipsis()
		.stage
			&.session
				height: 48px
				padding: 0 4px 0 8px
				display: flex
				align-items: center
				&::after
					content: 'soon'
					display: block
					position: absolute
					right: 4px
					top: 2px
					color: $clr-primary-text-dark
					background-color: $clr-blue-grey-500
					border-radius: 4px
					line-height: 18px
					padding: 0 4px
				&.has-image::after
					right: auto
					left: 4px
				&.live::after
					content: 'live'
					background-color: $clr-danger
				img
					flex: none
					height: 36px
					width: @height
					border-radius: 50%
					margin-right: 4px
				.info
					flex: auto
					display: flex
					flex-direction: column
					width: calc(100% - 40px)
					justify-content: center
				.title
					ellipsis()
					line-height: 24px
				&:not(.has-image) .title
					margin-right: 40px
				&:not(.has-image).live .title
					margin-right: 30px
				.subtitle
					display: flex
					justify-content: space-between
					line-height: 24px
					color: var(--clr-sidebar-text-disabled)
					.room
						display: flex
						line-height: 24px
						margin-right: 4px
						ellipsis()
						flex: 1
						max-width: max-content
						&::before
							content: '\F050D'
							font-family: "Material Design Icons"
							font-size: 18px
							line-height: 24px
							color: var(--clr-sidebar-text-disabled)
							margin-right: 4px
				.speakers
					ellipsis()
					flex: 1
					max-width: max-content
			&:not(.session)
				.room-icon::before
					content: '\F050D'
		.text-chat
			.room-icon::before
				content: '\F0423'
		.video-chat
			.room-icon::before
				content: '\F05A0'
		.direct-message, .text-chat, .video-chat
			padding-right: 8px
			display: flex
			align-items: flex-start
			.activity-icon
				margin-left: auto
				margin-right: 4px
				&::before
					opacity: 0.5 // TODO do a proper color variable for this
			.bunt-icon-button
				icon-button-style(color: var(--clr-sidebar-text-primary), style: clear)
				margin-left: auto
			&:not(:hover) .bunt-icon-button
				display: none
		#btn-browse-channels-trailing
			color: var(--clr-sidebar-text-secondary)
			background-color: transparent
			font-size: 12px
			font-weight: 500
			border-radius: 0
			&:hover:not(.disabled)
				background-color: var(--clr-sidebar-hover-bg)
	.admin
		> .router-link-active
				background-color: var(--clr-sidebar-active-bg)
				color: var(--clr-sidebar-text-primary)
	.buffer
		flex: auto
	> .profile
		display: flex
		padding: 8px
		align-items: center
		cursor: pointer
		color: var(--clr-sidebar-text-primary)
		&:hover
			background-color: rgba(255, 255, 255, 0.3)
		.c-avatar
			background-color: $clr-white
			border-radius: 50%
			padding: 4px
		.display-name
			flex: auto
			font-weight: 600
			font-size: 18px
			margin-left: 8px
		.mdi
			font-size: 24px
			line-height: 1
#app:not(.override-sidebar-collapse) .c-rooms-sidebar
	+below('l')
		position: fixed
		left: 0
		top: 0
		z-index: 901
		width: var(--sidebar-width)
		height: var(--vh100)
		touch-action: pan-y
		> .c-scrollbars .scroll-content
			touch-action: pan-y
		&.sidebar-enter-active, &.sidebar-leave-active
			transition: transform .2s
		&.sidebar-enter, &.sidebar-leave-to
			transform: translateX(calc(-1 * var(--sidebar-width)))
</style>
