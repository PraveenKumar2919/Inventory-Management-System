// Minimal hand-rolled icon set (stroke-based, 24x24 viewbox) so the app
// doesn't need an extra icon-font dependency.

const base = {
  fill: "none",
  stroke: "currentColor",
  strokeWidth: 2,
  strokeLinecap: "round",
  strokeLinejoin: "round",
};

const wrap = (paths) => (props) => (
  <svg viewBox="0 0 24 24" {...base} {...props}>
    {paths}
  </svg>
);

export const IconDashboard = wrap(
  <>
    <rect x="3" y="3" width="7" height="9" rx="1.5" />
    <rect x="14" y="3" width="7" height="5" rx="1.5" />
    <rect x="14" y="12" width="7" height="9" rx="1.5" />
    <rect x="3" y="16" width="7" height="5" rx="1.5" />
  </>
);

export const IconBox = wrap(
  <>
    <path d="M21 8 12 3 3 8v8l9 5 9-5V8Z" />
    <path d="M3 8l9 5 9-5" />
    <path d="M12 13v8" />
  </>
);

export const IconTag = wrap(
  <>
    <path d="M20.5 12.5 12 21 3 12l8.5-8.5H20a1 1 0 0 1 1 1v8.5Z" />
    <circle cx="15.5" cy="7.5" r="1.2" />
  </>
);

export const IconTruck = wrap(
  <>
    <rect x="1" y="6" width="13" height="10" rx="1" />
    <path d="M14 10h4l3 3v3h-7z" />
    <circle cx="5.5" cy="18" r="1.6" />
    <circle cx="16.5" cy="18" r="1.6" />
  </>
);

export const IconSwap = wrap(
  <>
    <path d="M4 8h13l-3-3" />
    <path d="M20 16H7l3 3" />
  </>
);

export const IconUsers = wrap(
  <>
    <circle cx="9" cy="8" r="3.2" />
    <path d="M2.5 20c.9-3.6 3.4-5.5 6.5-5.5s5.6 1.9 6.5 5.5" />
    <circle cx="17.5" cy="8.5" r="2.4" />
    <path d="M15.7 14.7c2.4.3 4 1.9 4.7 5.3" />
  </>
);

export const IconClipboard = wrap(
  <>
    <rect x="5" y="4" width="14" height="17" rx="2" />
    <path d="M9 4V3a1 1 0 0 1 1-1h4a1 1 0 0 1 1 1v1" />
    <path d="M8.5 11h7M8.5 15h7M8.5 19h4" />
  </>
);

export const IconChart = wrap(
  <>
    <path d="M4 20V10M11 20V4M18 20v-7" />
    <path d="M2 20h20" />
  </>
);

export const IconChevron = wrap(<path d="M9 6l6 6-6 6" className="chev" />);
export const IconChevronDown = wrap(<path d="M6 9l6 6 6-6" />);
export const IconSearch = wrap(
  <>
    <circle cx="11" cy="11" r="7" />
    <path d="M21 21l-4.35-4.35" />
  </>
);
export const IconPlus = wrap(
  <>
    <path d="M12 5v14M5 12h14" />
  </>
);
export const IconEdit = wrap(
  <>
    <path d="M12 20h9" />
    <path d="M16.5 3.5a2.12 2.12 0 0 1 3 3L7 19l-4 1 1-4L16.5 3.5Z" />
  </>
);
export const IconTrash = wrap(
  <>
    <path d="M3 6h18" />
    <path d="M8 6V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2" />
    <path d="M19 6l-1 14a2 2 0 0 1-2 2H8a2 2 0 0 1-2-2L5 6" />
    <path d="M10 11v6M14 11v6" />
  </>
);
export const IconX = wrap(
  <>
    <path d="M18 6 6 18M6 6l12 12" />
  </>
);
export const IconLogout = wrap(
  <>
    <path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4" />
    <path d="M16 17l5-5-5-5" />
    <path d="M21 12H9" />
  </>
);
export const IconMenu = wrap(
  <>
    <path d="M3 6h18M3 12h18M3 18h18" />
  </>
);
export const IconAlert = wrap(
  <>
    <path d="M10.3 3.9 1.9 18a1.5 1.5 0 0 0 1.3 2.2h17.6a1.5 1.5 0 0 0 1.3-2.2L13.7 3.9a1.5 1.5 0 0 0-2.6 0Z" />
    <path d="M12 9v4M12 17h.01" />
  </>
);
export const IconCheck = wrap(<path d="M20 6 9 17l-5-5" />);
export const IconInfo = wrap(
  <>
    <circle cx="12" cy="12" r="9" />
    <path d="M12 11v5.5M12 8v.01" />
  </>
);
export const IconEye = wrap(
  <>
    <path d="M1 12s4-7 11-7 11 7 11 7-4 7-11 7-11-7-11-7Z" />
    <circle cx="12" cy="12" r="3" />
  </>
);
export const IconPackageX = wrap(
  <>
    <path d="M21 8 12 3 3 8v8l9 5 9-5V8Z" />
    <path d="M3 8l9 5 9-5" />
    <path d="M12 13v8" />
    <path d="M8.5 6.3 15.5 10" />
  </>
);
export const IconArrowUpRight = wrap(<path d="M7 17 17 7M7 7h10v10" />);
export const IconFilter = wrap(<path d="M4 5h16l-6.5 8v6l-3 1.5v-7.5L4 5Z" />);
export const IconRefresh = wrap(
  <>
    <path d="M3 12a9 9 0 0 1 15.3-6.4L21 8" />
    <path d="M21 3v5h-5" />
    <path d="M21 12a9 9 0 0 1-15.3 6.4L3 16" />
    <path d="M3 21v-5h5" />
  </>
);
export const IconCalendar = wrap(
  <>
    <rect x="3" y="5" width="18" height="16" rx="2" />
    <path d="M8 3v4M16 3v4M3 10h18" />
  </>
);
export const IconReceipt = wrap(
  <>
    <path d="M6 2h12v20l-3-2-3 2-3-2-3 2Z" />
    <path d="M9 8h6M9 12h6M9 16h4" />
  </>
);
