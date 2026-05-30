import { Bell, Check, Clock, Inbox, X } from 'lucide-react';
import { Link } from 'react-router';

import { Button } from '~/components/ui/button';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuTrigger,
} from '~/components/ui/dropdown-menu';
import {
  useAcceptProjectInvitation,
  useDeclineProjectInvitation,
  useGetProjectInvitations,
  useGetProjectNotifications,
  useMarkProjectNotificationRead,
} from '~/features/projects/project.hooks';

function fmt(date: Date | string) {
  return new Intl.DateTimeFormat(undefined, {
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  }).format(new Date(date));
}

export function ProjectNotificationBell() {
  const { data: invitations = [] } = useGetProjectInvitations();
  const { data: notifications = [] } = useGetProjectNotifications();
  const acceptInvitation = useAcceptProjectInvitation();
  const declineInvitation = useDeclineProjectInvitation();
  const markRead = useMarkProjectNotificationRead();

  const pendingAccessIds = new Set(invitations.map((invitation) => invitation.id));
  const visibleNotifications = notifications.filter(
    (item) => !(item.type === 'PROJECT_INVITATION' && item.access_id && pendingAccessIds.has(item.access_id))
  );
  const unreadNotifications = visibleNotifications.filter((item) => !item.read_at);
  const totalPending = invitations.length + unreadNotifications.length;
  const hasItems = invitations.length > 0 || visibleNotifications.length > 0;

  return (
    <DropdownMenu>
      <DropdownMenuTrigger asChild>
        <button
          aria-label="Project notifications"
          className="relative flex h-7 w-7 items-center justify-center rounded-[7px] border border-neutral-800 text-neutral-400 transition-colors hover:border-neutral-700 hover:bg-neutral-900 hover:text-white"
        >
          <Bell className="h-3.5 w-3.5" />
          {totalPending > 0 && (
            <span className="absolute -right-1 -top-1 flex min-w-4 items-center justify-center rounded-full border border-black bg-amber-400 px-1 text-[9px] font-semibold leading-4 text-black">
              {totalPending > 9 ? '9+' : totalPending}
            </span>
          )}
        </button>
      </DropdownMenuTrigger>

      <DropdownMenuContent
        align="end"
        sideOffset={8}
        className="w-[360px] border border-neutral-800 bg-neutral-950 p-0 text-neutral-100 shadow-2xl"
      >
        <div className="flex items-center justify-between border-b border-neutral-900 px-3 py-2.5">
          <div>
            <p className="text-sm font-medium text-white">Project notifications</p>
            <p className="text-[11px] text-neutral-500">{invitations.length} pending invitation{invitations.length === 1 ? '' : 's'}</p>
          </div>
          <Link
            to="/projects-management"
            className="rounded-md border border-neutral-800 px-2 py-1 text-[11px] text-neutral-400 transition-colors hover:border-neutral-700 hover:text-white"
          >
            Projects
          </Link>
        </div>

        <div className="max-h-[420px] overflow-y-auto p-2">
          {!hasItems ? (
            <div className="flex flex-col items-center justify-center py-8 text-center">
              <Inbox className="h-5 w-5 text-neutral-700" />
              <p className="mt-2 text-sm text-neutral-500">No notifications yet</p>
              <p className="mt-1 max-w-[240px] text-xs leading-relaxed text-neutral-600">
                Invitations and access updates will show here as soon as they arrive.
              </p>
            </div>
          ) : (
            <div className="space-y-2">
              {invitations.map((invitation) => (
                <div key={invitation.id} className="rounded-lg border border-amber-500/20 bg-amber-500/5 p-3">
                  <div className="flex items-start gap-2">
                    <Clock className="mt-0.5 h-4 w-4 shrink-0 text-amber-400" />
                    <div className="min-w-0 flex-1">
                      <p className="truncate text-sm font-medium text-white">
                        {invitation.project_name ?? 'Project invitation'}
                      </p>
                      <p className="mt-1 text-xs leading-relaxed text-neutral-400">
                        Invited as <span className="text-neutral-200">{invitation.access_level}</span>
                        {invitation.can_clone ? ' with clone access.' : '.'}
                      </p>
                      <div className="mt-3 flex items-center gap-2">
                        <Button
                          size="xs"
                          onClick={() => acceptInvitation.mutate(invitation.id)}
                          disabled={acceptInvitation.isPending || declineInvitation.isPending}
                        >
                          <Check className="h-3 w-3" />
                          Accept
                        </Button>
                        <Button
                          size="xs"
                          variant="outline"
                          onClick={() => declineInvitation.mutate(invitation.id)}
                          disabled={acceptInvitation.isPending || declineInvitation.isPending}
                        >
                          <X className="h-3 w-3" />
                          Decline
                        </Button>
                      </div>
                    </div>
                  </div>
                </div>
              ))}

              {visibleNotifications.slice(0, 8).map((notification) => (
                <button
                  key={notification.id}
                  onClick={() => !notification.read_at && markRead.mutate(notification.id)}
                  className={`w-full rounded-lg border p-3 text-left transition-colors ${
                    notification.read_at
                      ? 'border-neutral-900 bg-black/20'
                      : 'border-neutral-800 bg-black/40 hover:border-neutral-700'
                  }`}
                >
                  <div className="flex items-start justify-between gap-3">
                    <div className="min-w-0">
                      <p className="truncate text-sm font-medium text-white">{notification.title}</p>
                      <p className="mt-1 line-clamp-2 text-xs leading-relaxed text-neutral-500">{notification.message}</p>
                    </div>
                    {!notification.read_at && <span className="mt-1 h-1.5 w-1.5 shrink-0 rounded-full bg-emerald-400" />}
                  </div>
                  <p className="mt-2 text-[10px] text-neutral-600">{fmt(notification.created_at)}</p>
                </button>
              ))}
            </div>
          )}
        </div>
      </DropdownMenuContent>
    </DropdownMenu>
  );
}
