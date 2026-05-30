import { Bell, Check, Clock, Inbox, X } from 'lucide-react';

import { Button } from '~/components/ui/button';
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

export function ProjectNotifications() {
  const { data: invitations = [], isLoading: loadingInvitations } = useGetProjectInvitations();
  const { data: notifications = [], isLoading: loadingNotifications } = useGetProjectNotifications();
  const acceptInvitation = useAcceptProjectInvitation();
  const declineInvitation = useDeclineProjectInvitation();
  const markRead = useMarkProjectNotificationRead();

  const pendingAccessIds = new Set(invitations.map((invitation) => invitation.id));
  const visibleNotifications = notifications.filter(
    (item) => !(item.type === 'PROJECT_INVITATION' && item.access_id && pendingAccessIds.has(item.access_id))
  );
  const unread = visibleNotifications.filter((item) => !item.read_at).length;
  const isEmpty = invitations.length === 0 && visibleNotifications.length === 0;

  return (
    <section className="rounded-lg border border-neutral-800 bg-neutral-950/70">
      <div className="flex items-center justify-between border-b border-neutral-900 px-4 py-3">
        <div className="flex items-center gap-2">
          <Bell className="h-4 w-4 text-neutral-500" />
          <h2 className="text-sm font-medium text-white">Notifications</h2>
          {unread > 0 && (
            <span className="rounded-md border border-amber-500/20 bg-amber-500/10 px-1.5 py-0.5 text-[10px] font-medium text-amber-400">
              {unread} unread
            </span>
          )}
        </div>
        <span className="text-xs text-neutral-600">{invitations.length} pending</span>
      </div>

      <div className="max-h-[360px] overflow-y-auto p-3">
        {(loadingInvitations || loadingNotifications) && isEmpty ? (
          <div className="space-y-2">
            {Array.from({ length: 3 }).map((_, index) => (
              <div key={index} className="h-16 rounded-lg animate-shimmer" />
            ))}
          </div>
        ) : isEmpty ? (
          <div className="flex flex-col items-center justify-center py-10 text-center">
            <Inbox className="h-6 w-6 text-neutral-700" />
            <p className="mt-2 text-sm text-neutral-500">No project notifications</p>
            <p className="mt-1 text-xs text-neutral-600">Invitations also appear in the top bar bell.</p>
          </div>
        ) : (
          <div className="space-y-2">
            {invitations.map((invitation) => (
              <div key={invitation.id} className="rounded-lg border border-amber-500/20 bg-amber-500/5 p-3">
                <div className="flex items-start gap-2">
                  <Clock className="mt-0.5 h-4 w-4 text-amber-400" />
                  <div className="min-w-0 flex-1">
                    <p className="truncate text-sm font-medium text-white">
                      {invitation.project_name ?? 'Project invitation'}
                    </p>
                    <p className="mt-1 text-xs text-neutral-400">
                      You were invited as <span className="text-neutral-200">{invitation.access_level}</span>
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

            {visibleNotifications.map((notification) => (
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
                  {!notification.read_at && <span className="mt-1 h-1.5 w-1.5 rounded-full bg-emerald-400" />}
                </div>
                <p className="mt-2 text-[10px] text-neutral-600">{fmt(notification.created_at)}</p>
              </button>
            ))}
          </div>
        )}
      </div>
    </section>
  );
}
